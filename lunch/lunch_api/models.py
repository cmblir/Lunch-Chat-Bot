from django.db import models

# Create your models here.
class Species(models.Model):
    name = models.CharField(max_length=100)
    classification = models.CharField(max_length=100)
    language = models.CharField(max_length=100)

    #foreignkey 설정할 때 web에서 primary key의 name으로 보여주게됨. but db에는 id로 저장됨
    #아니면 primary key 그대로 1번 2번 이렇게 보임. 
    def __str__(self):
       return self.name
       
class Person(models.Model):
   name = models.CharField(max_length=100)
   birth_year = models.CharField(max_length=10)
   eye_color = models.CharField(max_length=10)
   species = models.ForeignKey(Species, on_delete=models.DO_NOTHING)
