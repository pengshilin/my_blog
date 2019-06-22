from django.db import models
from django.contrib.auth.models import User
#引入内置信号
from django.db.models.signals import post_save
#引入信号接收器的装饰器
from django.dispatch import receiver

#用户扩展信息
class Profile(models.Model):
    #与 User 模型构成一对一的关系,用法：
    # user = models.OneToOneField(to, on_delete, parent_link=False, options),第一位置参数为关联的模型，如果没有指定related_name,Django将使用当前模型的小写名作为默认值
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    #电话号码字段，NULL = True : null 是针对数据库而言，，如果null=True，表示数据库的该字段可以为空，即在Null字段显示YES
    #blank=True:blank是针对表单的，表示你的表单填写该字段时候可以不填，但是对数据库来说，没有任何影响
    phone = models.CharField(max_length=20, blank=True)
    #头像，upload_to指定了图片上传的位置，即'avatar/%Y%m%d/'，%Y%m%d/是日期格式化的写法，会最终格式化为系统时间，注意ImageField字段不会存储图片本身，而仅仅保存图片的地址
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    #个人简介
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return 'user {}'.format(self.user.username) #{}.format()，格式化字符串,用法和 % 一样

#信号接受函数，每当新建 User实例时自动调用
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

#信号接受函数，每当更新 User 实例时自动调用
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()