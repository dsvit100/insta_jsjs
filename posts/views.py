from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# 딕셔너리를 json으로 바꿔주는 라이브러리

# Create your views here.

def index(request):
    posts = Post.objects.all()
    form = CommentForm()

    context = {
        'posts': posts,
        'form': form,
    }
    return render(request, 'index.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES) # 사진 데이터도 같이 넣기 위해서 두번째 인자 작성
        if form.is_valid():
            post = form.save(commit=False) # 이 게시물을 누가 저장했는지의 유저정보가 빠져있음음
            post.user = request.user
            form.save()
            return redirect('posts:index')

    else:
        form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'create.html', context)


@login_required
def comment_create(request, post_id):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user # 유저 정보를 넣어야하고
        comment.post_id = post_id # 게시물 정보를 넣어야 함
        comment.save() # 다 넣었으니 저장
        return redirect('posts:index')

@login_required
def like(request, post_id):
    # 현재 로그인 한 사람, 어떤 게시물을 (좋아요 눌렀는지)
    user = request.user
    post = Post.objects.get(id=post_id)
    # 중간 테이블
    # if post in user.like_posts.all(): # user가 좋아요를 누른 포스트 중에 이 포스트가 있닝
    # 만약 user가 이 게시글에 좋아요 버튼을 누른 사람들 리스트에 들어있다면 
    if user in post.like_users.all():
        # user.like_posts.remove(post)
        post.like_users.remove(user)
    else:
        # user.like_posts.add(post) # 좋아요를 받은 게시글 목록에 이 게시글을 추가해
        post.like_users.add(user) # 좋아요를 한 사람들 목록에 이 user를 추가해 
    return redirect('posts:index')


def feed(request):
    followings = request.user.followings.all() # request.user = 지금 로그인한 사람이 / .followings 팔로우하고 있는 사람들 / all 모두
    posts = Post.objects.filter(user__in=followings) # user 컬럼에 오른쪽 followings에 포함된 사람들을 찾음
    form = CommentForm()

    context = {
        'posts': posts,
        'form': form,
    }
    return render(request, 'index.html', context)



def like_async(request, id):
    user = request.user
    post = Post.objects.get(id=id)
    
    if user in post.like_users.all():
        post.like_users.remove(user)
        status = False
    else:
        post.like_users.add(user)
        status = True

# 좋아요 버튼이 추가된 부분만 json 구조로 남겨줄 것
    context = {
        'post_id': id,
        'status': status,
        # true 혹은 false가 들어가있음
    }

    return JsonResponse(context)