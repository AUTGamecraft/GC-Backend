from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Renames a Django project'

    def add_arguments(self , parser):
        parser.add_argument('pr_name' , type=str , help='The previous Django project name')
        parser.add_argument('n_name' , type=str , help='The new Django project name')
        
    def handle(self , *args , **kwargs):
        n_name = kwargs['n_name']
        pr_name = kwargs['pr_name']


        # bit of logic to rename the project

        files_to_reanme = [
            f'{pr_name}/settings/base.py'
            ,f'{pr_name}/wsgi.py'
            ,'manage.py'
            ]
        folder_to_rename = pr_name


        for f in files_to_reanme:
            with open(f,'r') as file:
                file_data = file.read()

            file_data = file_data.replace( pr_name , n_name)

            with open(f , 'w') as file:
                file.write(file_data)

        os.rename(folder_to_rename , n_name)

        self.stdout.write(self.style.SUCCESS(f'Project has been renamed from {pr_name} to {n_name}'))