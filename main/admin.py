from django.contrib import admin
from .models import Category, Size, Product, \
  ProductSize, ProductImage

# Register your models here.


# чтобы вывести модель ProductImage на странице (модели) Product
# проще говоря нащи классы - модели. И есть общая модель - Product, 
# внутри которой есть модели такие как productImage - то есть это класс, 
# который на вход принимает картинки товара
class ProductImageInline(admin.TabularInline):
  model = ProductImage
  extra = 1 # сколько изначально будет полей во вкладке добавления товаров


class ProductSizeInline(admin.TabularInline):
  model = ProductSize
  extra = 1



class ProductAdmin(admin.ModelAdmin):
  list_display = ['name', 'category', 'color', 'price'] # основные парамтеры из класса Product из файла models.py # лист дисплей видим при заходе на главную страницу со всеми продуктами
  list_filter = ['category', 'color'] # фильтр по
  search_fields = ['name', 'color', 'description'] # поиск по
  prepopulated_fields = {'slug' : ('name',)} # инициализируем кортеж. Обязательно ставим запятую, если в кортеже 1 элемент
  inlines = [ProductImageInline, ProductSizeInline]


class CategoryAdmin(admin.ModelAdmin):
  list_display = ['name', 'slug']
  prepopulated_fields = {'slug' : ('name',)}


class SizeAdmin(admin.ModelAdmin):
  list_display = ['name']

# регистрируем прописанные выше классы в админке
admin.site.register(Category, CategoryAdmin) # берём модель Category и привязывает ей настройки CategoryAdmin
admin.site.register(Size, SizeAdmin)
admin.site.register(Product, ProductAdmin)


