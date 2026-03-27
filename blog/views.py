from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CommentForm, PostForm, RegisterForm
from .models import Like, Post


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        context["comments"] = post.comments.select_related("author").all()
        context["comment_form"] = kwargs.get("comment_form") or CommentForm()
        context["like_count"] = post.likes.count()
        context["has_liked"] = (
            self.request.user.is_authenticated
            and Like.objects.filter(post=post, user=self.request.user).exists()
        )
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Handle comment submissions from the post detail page.
        self.object = self.get_object()
        post = self.object

        if "comment_submit" not in request.POST:
            return redirect("blog:post_detail", pk=post.pk)

        if not request.user.is_authenticated:
            login_url = reverse("blog:login")
            return redirect(f"{login_url}?{urlencode({'next': request.path})}")

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("blog:post_detail", pk=post.pk)

        return self.render_to_response(
            self.get_context_data(comment_form=form, **kwargs)
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect("blog:post_detail", pk=self.kwargs["pk"])


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect("blog:post_detail", pk=self.kwargs["pk"])


@login_required
def toggle_like(request: HttpRequest, pk: int):
    post = get_object_or_404(Post, pk=pk)
    like = Like.objects.filter(post=post, user=request.user).first()
    if like:
        like.delete()
    else:
        Like.objects.create(post=post, user=request.user)
    return redirect("blog:post_detail", pk=pk)


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("blog:post_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("blog:post_list")
    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


def login_user(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("blog:post_list")

    next_url = request.GET.get("next") or request.POST.get("next") or "/"

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "registration/login.html",
        {"form": form, "next": next_url},
    )


def logout_user(request: HttpRequest) -> HttpResponse:
    # Support both link click (GET) and form submit (POST).
    logout(request)
    return redirect("blog:post_list")
