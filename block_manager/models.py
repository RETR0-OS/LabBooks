from django.db import models
from course_manager.models import LabBooks
# Create your models here.

class MarkdownBlock(models.Model):
    linked_notebook = models.ForeignKey(LabBooks, on_delete=models.CASCADE)
    block_order = models.IntegerField()
    block_content = models.TextField()

    def __str__(self):
        return self.linked_notebook.course.code + " - " + str(self.block_order)

class CodeBlock(models.Model):
    linked_notebook = models.ForeignKey(LabBooks, on_delete=models.CASCADE)
    block_order = models.IntegerField()
    block_content = models.TextField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.linked_notebook.course.code + " - " + str(self.block_order)


class McqBlock(models.Model):
    linked_notebook = models.ForeignKey(LabBooks, on_delete=models.CASCADE)
    block_order = models.IntegerField()
    block_question = models.TextField()
    block_option_1 = models.TextField()
    block_option_2 = models.TextField()
    block_option_3 = models.TextField()
    block_option_4 = models.TextField()
    block_answer = models.IntegerField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.linked_notebook.course.code + " - " + str(self.block_order)


class CodeTestCases(models.Model):
    linked_code_assignment = models.ForeignKey(CodeBlock, on_delete=models.CASCADE)
    case_input = models.TextField()
    case_output = models.TextField()

    def __str__(self):
        return self.linked_code_assignment.linked_notebook.course.code + " - " + str(self.linked_code_assignment.block_order)
