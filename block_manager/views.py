from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from course_manager.models import Course, LabBooks
from accounts.models import UserProfile
from block_manager.models import MarkdownBlock, CodeBlock, McqBlock
from itertools import chain
from RestrictedPython import compile_restricted, safe_globals, utility_builtins
from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getiter
import resource
# Create your views here.

@api_view(['GET'])
def load_student_notebook(request, course_code, notebook_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='student')
        course = Course.objects.get(code=course_code)
        notebook = LabBooks.objects.get(course=course, id=notebook_id, published=True)
        markdownBlocks = MarkdownBlock.objects.filter(linked_notebook=notebook)
        codeBlocks = CodeBlock.objects.filter(linked_notebook=notebook)
        mcqBlocks = McqBlock.objects.filter(linked_notebook=notebook)
        filteredMcqBlocks = []
        for block in mcqBlocks:
            filteredMcqBlocks.append({
                'id': block.id,
                'order': block.block_order,
                'question': block.block_question,
                'option_1': block.block_option_1,
                'option_2': block.block_option_2,
                'option_3': block.block_option_3,
                'option_4': block.block_option_4,
                'completed': block.completed
            })
        data_blocks = list(chain(markdownBlocks, codeBlocks, filteredMcqBlocks))

        data = {
            "course": course,
            "notebook": notebook,
            "data_blocks": data_blocks
        }
        return Response(data, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Only students can view lab books'}, status=status.HTTP_403_FORBIDDEN)
    except LabBooks.DoesNotExist:
        return Response({'error': 'Lab book does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def load_teacher_notebook(request, course_code, notebook_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='teacher')
        course = Course.objects.get(code=course_code, teacher=request.user)
        notebook = LabBooks.objects.get(course=course, id=notebook_id)
        markdownBlocks = MarkdownBlock.objects.filter(linked_notebook=notebook)
        codeBlocks = CodeBlock.objects.filter(linked_notebook=notebook)
        mcqBlocks = McqBlock.objects.filter(linked_notebook=notebook)
        data_blocks = list(chain(markdownBlocks, codeBlocks, mcqBlocks))
        data = {
            "course": course,
            "notebook": notebook,
            "data_blocks": data_blocks
        }
        return Response(data, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Only teachers can view lab books'}, status=status.HTTP_403_FORBIDDEN)
    except LabBooks.DoesNotExist:
        return Response({'error': 'Lab book does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_notebook(request, course_code):
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='teacher')
        course = Course.objects.get(code=course_code, teacher=request.user)
        notebook = LabBooks.objects.create(course=course, owner=request.user, owner_role='teacher', author=request.user)
        notebook.save()
        return Response({'message': 'Notebook created successfully'}, status=status.HTTP_201_CREATED)
    except Course.DoesNotExist:
        return Response({'error': 'Course does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Only teachers can create lab books'}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def delete_notebook(request, course_code, notebook_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='teacher')
        course = Course.objects.get(code=course_code, teacher=request.user)
        notebook = LabBooks.objects.get(course=course, id=notebook_id, owner=request.user, owner_role='teacher')
        notebook.delete()
        return Response({'message': 'Notebook deleted successfully'}, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Only teachers can delete lab books'}, status=status.HTTP_403_FORBIDDEN)
    except LabBooks.DoesNotExist:
        return Response({'error': 'Lab book does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def update_teacher_notebooks(request, course_code, notebook_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='teacher')
        course = Course.objects.get(code=course_code, teacher=request.user)
        notebook = LabBooks.objects.get(course=course, id=notebook_id, owner=request.user, owner_role='teacher')
        if notebook.published:
            return Response({'error': 'Notebook is published and cannot be edited'}, status=status.HTTP_403_FORBIDDEN)
        data_blocks = request.data.get('data_blocks')

        mcq_blocks = McqBlock.objects.filter(linked_notebook=notebook)
        code_blocks = CodeBlock.objects.filter(linked_notebook=notebook)
        markdown_blocks = MarkdownBlock.objects.filter(linked_notebook=notebook)

        mcq_blocks.delete()
        code_blocks.delete()
        markdown_blocks.delete()

        for block in data_blocks:
            if block['type'] == 'markdown':
                markdown_block = MarkdownBlock.objects.create(id=block['id'], linked_notebook=notebook, block_order=block['index'], block_content=block['content'])
                markdown_block.save()
            elif block['type'] == 'code':
                code_block = CodeBlock.objects.create(id=block['id'], linked_notebook=notebook, block_order=block['index'], block_content=block['content'])
                code_block.save()
            elif block['type'] == 'mcq':
                mcq_block = McqBlock.objects.get(id=block['id'], linked_notebook=notebook, block_question=block['question'], block_order=block['index'], block_option_1=block['option_1'], block_option_2=block['option_2'], block_option_3=block['option_3'], block_option_4=block['option_4'], block_answer=block['answer'])
                mcq_block.save()
        return Response({'message': 'Notebook updated successfully'}, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Only teachers can edit lab books'}, status=status.HTTP_403_FORBIDDEN)
    except LabBooks.DoesNotExist:
        return Response({'error': 'Lab book does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_accessible_notebooks(request, course_code):
    try:
        user_profile = UserProfile.objects.get(user=request.user, courses=course_code)
        course = Course.objects.get(code=course_code)

        if user_profile.role == 'teacher':
            lab_books = LabBooks.objects.filter(course=course, owner = request.user, owner_role='teacher')
        else:
            lab_books = LabBooks.objects.filter(course=course, owner = request.user, owner_role='student', published=True)
        data = {
            "course": course,
            "notebooks": lab_books
        }
        return Response(data, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'You do not have access to this course'}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def grade_mcq_question(request, notebook_id, block_id):
    try:
        notebook = LabBooks.objects.get(id=notebook_id, owner=request.user, owner_role='student', published=True)
        mcq_block = McqBlock.objects.get(id=block_id, linked_notebook=notebook)
        answer = request.data.get('answer')
        if answer == mcq_block.block_answer:
            mcq_block.completed = 1
            mcq_block.save()
            return Response({'message': True}, status=status.HTTP_200_OK)
        else:
            mcq_block.completed = 0
            mcq_block.save()
            return Response({'message': False}, status=status.HTTP_200_OK)

    except McqBlock.DoesNotExist:
        return Response({'error': 'Question does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except LabBooks.DoesNotExist:
        return Response({'error': 'Notebook does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def code_grader(request, notebook_id, block_id):
    try:
        notebook = LabBooks.objects.get(id=notebook_id, owner=request.user, owner_role='student', published=True)
        code_block = CodeBlock.objects.get(id=block_id, linked_notebook=notebook)
        code = request.data.get('block_content')

        # Define a safe execution environment
        restricted_globals = safe_globals.copy()
        restricted_globals['__builtins__'] = utility_builtins
        restricted_globals['_getitem_'] = default_guarded_getitem
        restricted_globals['_getiter_'] = default_guarded_getiter

        # Compile the code in a restricted environment
        byte_code = compile_restricted(code, '<string>', 'exec')

        # Set resource limits (e.g., CPU time, memory usage)
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))  # 1 second of CPU time
        resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 256, 1024 * 1024 * 256))  # 128 MB of memory

        # Execute the code in the restricted environment
        exec(byte_code, restricted_globals)

        # Check the output against the expected answer
        if restricted_globals.get('output') == code_block.block_answer:
            code_block.completed = 1
            code_block.save()
            return Response({'message': True}, status=status.HTTP_200_OK)
        else:
            code_block.completed = 0
            code_block.save()
            return Response({'message': False}, status=status.HTTP_200_OK)

    except CodeBlock.DoesNotExist:
        return Response({'error': 'Question does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except LabBooks.DoesNotExist:
        return Response({'error': 'Notebook does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def publish_notebook(request, course_code, notebook_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user, role='teacher')
        course = Course.objects.get(code=course_code, teacher=request.user)
        notebook = LabBooks.objects.get(course=course, id=notebook_id)
        if notebook.published:
            return Response({'error': 'Notebook is already published'}, status=status.HTTP_403_FORBIDDEN)
        notebook.published = True
        notebook.save()

        students = UserProfile.objects.filter(courses=course, role='student')
        for student in students:
            student_notebook_creator(request, student, course, notebook)
        return Response({'message': 'Notebook published successfully'}, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Only teachers can publish lab books'}, status=status.HTTP_403_FORBIDDEN)
    except LabBooks.DoesNotExist:
        return Response({'error': 'Lab book does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def student_notebook_creator(request, student, course, template_notebook):
    try:
        notebook = LabBooks.objects.create(course=course, owner=student, owner_role='student', author=request.user, published=True)
        notebook.save()
        markdownBlocks = MarkdownBlock.objects.filter(linked_notebook=template_notebook)
        codeBlocks = CodeBlock.objects.filter(linked_notebook=template_notebook)
        mcqBlocks = McqBlock.objects.filter(linked_notebook=template_notebook)
        for block in markdownBlocks:
            new_block = MarkdownBlock.objects.create(linked_notebook=notebook, block_order=block.block_order, block_content=block.block_content)
            new_block.save()
        for block in codeBlocks:
            new_block = CodeBlock.objects.create(linked_notebook=notebook, block_order=block.block_order, block_content=block.block_content, completed=False)
            new_block.save()
        for block in mcqBlocks:
            new_block = McqBlock.objects.create(linked_notebook=notebook, block_order=block.block_order, block_question=block.block_question, block_option_1=block.block_option_1, block_option_2=block.block_option_2, block_option_3=block.block_option_3, block_option_4=block.block_option_4, block_answer=block.block_answer, completed=False)
            new_block.save()
        return
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
