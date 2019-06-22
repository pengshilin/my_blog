from django.db import models

from django.contrib.auth.models import User

from django.utils import timezone   #timezone 用于处理时间相关事务

from django.urls import reverse

class ArticleColumn(models.Model):
    """栏目的 Model"""
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


#博客文章数据类型
class ArticlePost(models.Model):
    #文章作者，在船舰多对一的关系中，需要在外键的第二个参数中on_delete=models.CASCADE 主外关系键中，级联删除，也就是删除主表的数据的时候从表中的数据页随着一起删除
    #使用ForeignKey 定义一个关系，这将告诉Django，每个（或多个）ArticlePost 对象都关联到一个User对象
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    #文章标题，models.CharFiled 为字符串字段，用于保存较短的字符串，比如标题
    title = models.CharField(max_length=100)

    #文章正文，保存大量文本使用TextFiled
    body = models.TextField()

    #文章创建时间,参数 default=timezone.now 指定其在创建数据时将默认写入当前的时间
    created = models.DateTimeField(default=timezone.now)

    #文章更新时间,参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)
    #存储浏览量，PositiveIntegerField 是用于存储正整数的字段，default=0设定初始值从0开始
    total_views = models.PositiveIntegerField(default=0)

    #文章栏目的 '一对多' 外键
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    #内部类Class Meta 用于给model 定义元数据
    class Meta:
        #ordering 指定模型返回的数据的排列顺序
        #'-created'表名数据应该以倒序排列
        ordering = ('-created',)

    def __str__(self):
        return self.title

    #获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])
