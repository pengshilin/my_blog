#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from django.urls import path
from . import views
app_name = 'article'    #正在部署的应用名称

urlpatterns = [
    #用户请求 aiticle/ 链接时，会调用views.py中的article_list 函数，并返回渲染后的对象，参数name用于反查url地址，相当于给url起了个名字
    path('article/', views.article_list, name='article_list'),
    path('article/detail<int:article_id>/', views.article_detail, name='article_detail'),
    path('article/create/',views.article_create,name='article_create'),
    path('article/delete<int:article_id>/', views.article_delete, name='article_delete'),
    path('article/update<int:article_id>/', views.article_update, name='article_update'),
]