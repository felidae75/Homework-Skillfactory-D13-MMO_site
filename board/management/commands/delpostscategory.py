from django.core.management.base import BaseCommand, CommandError
from ... models import *

class Command(BaseCommand):
    help = 'Удаляет все посты в категории. Аргумент - название категории'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        answer = input(f'Вы хотите удалить все статьи в категории {options["category"]}? y/n')

        if answer == 'y':
            try:
                category = Category.get(name=options['category'])
                Post.objects.filter(category == category).delete()
                self.stdout.write(self.style.SUCCESS(
                    f'Succesfully deleted all news from category {category.name}'))  # в случае неправильного подтверждения говорим, что в доступе отказано
            except Post.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Could not find category {}'))
        else:
            self.stdout.write(self.style.ERROR('Отменено'))