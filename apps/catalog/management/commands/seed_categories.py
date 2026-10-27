from django.core.management.base import BaseCommand
from apps.catalog.models import Category
class Command(BaseCommand):
 help='Create starter product categories without demo products or accounts'
 def handle(self,*args,**kwargs):
  for name,slug in [('Electronics','electronics'),('Fashion','fashion'),('Home & Kitchen','home-kitchen'),('Books','books'),('Sports','sports'),('Beauty','beauty')]:
   Category.objects.get_or_create(slug=slug,defaults={'name':name})
  self.stdout.write(self.style.SUCCESS('Starter categories ready'))
