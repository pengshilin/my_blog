from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost
import markdown
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q   #引入Q对象
from comment.models import Comment
from .models import ArticleColumn #引入栏目Model
#引入分页模块
from django.core.paginator import Paginator

def article_list(request):
    # return HttpResponse('hello world!')
#每一个视图表现为一个简单的python函数，它必须要做两件事：返回一个包含请求页面内容的HttpResponse对象，或者抛出一个异常
#视图函数中的 request 与网页发来的请求相关，里面包含 get\post的内容、用户浏览器、系统等信息，django调用article_list函数时返回一个HttpResponse对象

    search = request.GET.get('search')
    order = request.GET.get('order')

    #用户搜索逻辑
    if search:
        #根据 GET 请求中查询条件
        #返回不同排序的对象数组
        if order == 'total_views':
            #用 Q 对象，进行联合搜索
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        #将 search 参数重置为空
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()
    # article_list = ArticlePost.objects.all()    #取出所有博客文章
    #每页显示 1 篇文章
    paginator = Paginator(article_list, 3)
    # 获取 URL 中的页码
    page = request.GET.get('page')
    #将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)

    context = {'articles': articles, 'order': order, 'search':search }    #需要传递给模板 templeates 的对象
    # render 函数:载入模板，并返回 context 对象
    return render(request, 'article/list.html', context)

#文章详情
def article_detail(request, article_id):
    #取出响应的文章
    article = ArticlePost.objects.get(id=article_id)
    #取出文章评论
    comments = Comment.objects.filter(article=article_id)

    #浏览量 +1,  update_fields=[]  指定了数据库只更新total_views字段，优化执行效率
    article.total_views += 1
    article.save(update_fields=['total_views'])

    #将markdown 语法渲染成html样式
    md = markdown.Markdown(
        extensions = [
            #包含 缩写、表格等常用扩展
            'markdown.extensions.extra',
            #语法高亮扩展
            'markdown.extensions.codehilite',

            #目录扩展
            'markdown.extensions.toc',]
    )
    #用convert()方法将正文渲染为html 页面，通过md.toc 将目录传递给模板
    article.body = md.convert(article.body)

    #需要传递给模板的对象
    context = {'article': article, 'toc': md.toc, 'comments': comments}
    return render(request, 'article/detail.html', context)

#检查登录
@login_required(login_url='/userprofile/login/')
#写文章的视图
def article_create(request):
    #判断用户是否提交数据
    if request.method == 'POST':
        #将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        #判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            #保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            #如果你进行过删除数据库表的操作，可能会找不到 id=1 的作者
            #此时请重新创建用户,并指定目前登录的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            #将新文章保存到数据库中
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            #完成后返回到文章列表
            return redirect('article:article_list')
        #如果数据不合法，返回错误信息
        else:
            return HttpResponse('表单内容有误,请重新填写.')
    #如果用户请求获取数据
    else:
        #创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        #赋值上下文
        context = {'article_post_form': article_post_form, 'columns': columns }
        #返回模板
        return render(request, 'article/create.html', context)

@login_required(login_url='/userprofile/login/')
#删除文章
def article_delete(request, article_id):
    #根据id 获取需要删除的文章
    article = ArticlePost.objects.get(id=article_id)
    if request.user != article.author:
        return HttpResponse('抱歉, 你没有权限操作.')
    else:
        #调用 .delete() 方法删除文章
        article.delete()
        #完成删除后返回文章列表
        return redirect('article:article_list')

@login_required(login_url='/userprofile/login/')
#更新文章
def article_update(request,article_id):
    '''
    更新文章的视图函数通过POST方法提交表单，更新title\body 字段
    GET 方法进入初始表单页面，article_id 是文章的id
    :param request:
    :param article_id:
    :return:
    '''

    #获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=article_id)
    #过滤非作者的用户
    if request.user != article.author:
        return HttpResponse('抱歉，你无权修改这篇文章.')

    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        #判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            #保存新写入的 title \body ,数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.save()
            return redirect('article:article_detail', article_id=article_id)
        #如果数据不合法，返回错误信息
        else:
            return HttpResponse('表单内容有误，请重新填写')
    # GET请求
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        #赋值上下文，将article 文章对象页传进去，以便提取旧的内容
        context = {'article': article, 'article_post_form': article_post_form, 'columns': columns }
        return render(request, 'article/update.html', context)