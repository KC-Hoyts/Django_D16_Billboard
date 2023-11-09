from allauth.account.models import EmailAddress

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

from .models import *
from .filters import PostsFilter
from .forms import PostForm, CommentForm


class MyEmailAddressConfirmation(DetailView):
    model = User
    template_name = "account/email_confirm.html"

    def post(self, request, pk, **kwargs):
        entered_code = request.POST.get("code")
        user_id = User.objects.get(pk=pk).id
        user_code = RandomNumber.objects.get(related_user=user_id).number
        if int(entered_code) == user_code:
            RandomNumber.objects.get(related_user=user_id).delete()
            email_verified = EmailAddress.objects.get(user=user_id)
            email_verified.verified = True
            email_verified.save()
            return redirect("/success/")
        else:
            return redirect("/fail/")


class PostsList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    ordering = "-date_creation"
    paginate_by = 6


class PersonalPostsList(ListView):
    model = Post
    ordering = "-date_creation"
    template_name = 'myposts.html'

    def get(self, request):
        myposts = Post.objects.filter(author=User.objects.get(username=request.user))
        if len(myposts) == 0:
            context = {
                'Posts_no_exist': "_",
            }
        else:
            context = {
                'MyPosts': myposts,
                'posts_amount' : len(myposts)
            }
        return HttpResponse(render(request, 'myposts.html', context))


class PostView(DetailView):
    model = Post
    template_name = "one_post.html"

    def get(self, request, pk):
        context = {
            "comments" : Replies.objects.filter(comment_post=Post.objects.get(pk=pk)).values('id','date_creation',
                                                                                           'author__username',
                                                                                           'text', 'status').order_by('-date_creation'),
            "OnePost" : Post.objects.get(pk=pk),
            'comment_form' : CommentForm,
        }
        try:
            for com in Replies.objects.filter(comment_post=Post.objects.get(pk=pk)):
                if com.author == User.objects.get(username=request.user):
                    context['existing_comment'] = 'True'
                    if com.status == True:
                        context['reply_is_replied_on_email'] = 'На Ваш отклик ответили! Проверьте личную почту.'
        except:
            pass

        return HttpResponse(render(request, 'one_post.html', context))

    def post(self, request, pk, **kwargs):
        comment_id = request.POST.get('comment_id')
        action = request.POST.get('action')
        if action == 'delete_comment':
            #Если нажата кнопка action с атрибутом delete_comment, то удалить отклик из базы
            Replies.objects.get(id=comment_id).delete()
            return redirect('post_view', pk=pk)

        if action == 'reply_comment':
            #Если нажата с атрибутом reply_comment, то перенаправить на страницу ответа
            return redirect('reply_comment', pk=comment_id)

        else:
            #Иначе отправить данные с формы отклика
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.comment_post = Post.objects.get(pk=pk)
                new_comment.author = User.objects.get(username=request.user)
                new_comment.save()

                #Отправка отклика на почту автора
                if User.objects.get(username=Post.objects.get(pk=pk).author).email:
                    send_to = User.objects.get(username=Post.objects.get(pk=pk).author).email
                    subject = 'У вас новый отклик!'
                    text = f'Пользователь {new_comment.author} оставил отклик к Вашему объявлению {new_comment.comment_post}:' \
                           f'{new_comment.text}' \
                           f'' \
                           f'Отклик оставлен {new_comment.date_creation}' \
                           f'' \
                           f'Зайдите на сайт, чтобы ответить на отклик!'

                    html = (
                           f'Пользователь "{new_comment.author}" оставил отклик к Вашему объявлению "{new_comment.comment_post}":'
                           f'<br><br><i>"{new_comment.text}"</i><br>'
                           f''
                           f'<br>Отклик оставлен {new_comment.date_creation} <br>'
                           f''
                           f'Зайдите на сайт, чтобы ответить на отклик!111!!!!!!11'

                    )
                    msg = EmailMultiAlternatives(
                        subject=subject, body=text, from_email=None, to=[send_to]
                    )
                    msg.attach_alternative(html, "text/html")
                    msg.send()

            return redirect('post_view', pk=pk)


class PostSearch(ListView):
    model = Post
    ordering = '-date_creation'
    template_name = 'post_search.html'
    context_object_name = 'Post_search'
    paginate_by = PostsList.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['cat_list'] = Post.CATEGORY_LIST
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostsFilter(self.request.GET, queryset)
        return self.filterset.qs


class PostCreate(LoginRequiredMixin, CreateView):
    permission_required = ('board.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post            # также для этого класса переопределяем метод get_absolute_url в моделях
    template_name = "post_create.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView): #
    permission_required = ('board.change_post',)
    form_class = PostForm
    model = Post
    template_name = "post_edit.html"


class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('board.delete_post',)
    model = Post
    template_name = "post_delete.html"
    success_url = reverse_lazy('post_list')


class CommentReply(DetailView):
    model = Replies
    template_name = "reply_on_comment.html"
    context_object_name = "Reply"

    def get(self, request, pk):
        context = {
            "Reply" : Replies.objects.get(pk=pk),
            'comment_form' : CommentForm,
        }
        return HttpResponse(render(request, 'reply_on_comment.html', context))

    def post(self, request, pk, **kwargs):
        current_comment_id = request.POST.get('Reply_id') # id отклика на который отвечаем
        email_message_text = request.POST.get("response_text") # наше выгруженное с сайта сообщение котрое надо отправить на емэил

        #Отправка отклика на почту автора
        if User.objects.get(username=Replies.objects.get(pk=pk).author).email:
            reply_to_email = User.objects.get(username=Replies.objects.get(pk=pk).author).email
            replied_post = Post.objects.get(pk=Replies.objects.get(pk=pk).comment_post.id)

            subject = 'Вам ответили на отклик!'
            text = f'Ответ пользователя "{replied_post.author}" на Ваш отклик к посту "{replied_post.title}":' \
                   f'"{email_message_text}"' \
                   f'' \
                   f'' \
                   f'Свяжитесь с пользователем "{replied_post.author}" для дальнейшей беседы!'

            html = (
                f'Ответ пользователя "{replied_post.author}" на Ваш отклик к посту "{replied_post.title}":' 
                f'<br><br><i>"{email_message_text}"</i>'
                f''
                f''
                f'<br><br>Свяжитесь с пользователем "{replied_post.author}" для дальнейшей беседы!'
            )
            msg = EmailMultiAlternatives(
                subject=subject, body=text, from_email=None, to=[reply_to_email]
            )
            msg.attach_alternative(html, "text/html")
            msg.send()

        # меняем статус отклика на "отвеченный"
        comment_status = Replies.objects.get(id=current_comment_id)
        comment_status.status = True
        comment_status.save()
        return redirect('post_view', pk=comment_status.comment_post.id)






