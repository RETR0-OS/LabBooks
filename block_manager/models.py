from django.db import models
from course_manager.models import LabBooks
# Create your models here.

class markdownBlock(models.Model):
    linked_notebook = models.ForeignKey(LabBooks, on_delete=models.CASCADE)
    block_order = models.IntegerField()
    block_content = models.TextField()

    def __str__(self):
        return self.linked_notebook.course.code + " - " + str(self.block_order)


class mcqBlock(models.Model):
    linked_notebook = models.ForeignKey(LabBooks, on_delete=models.CASCADE)
    block_order = models.IntegerField()
    block_question = models.TextField()
    block_option_1 = models.TextField()
    block_option_2 = models.TextField()
    block_option_3 = models.TextField()
    block_option_4 = models.TextField()
    block_answer = models.IntegerField()

    def __str__(self):
        return self.linked_notebook.course.code + " - " + str(self.block_order)