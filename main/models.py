from django.db import models

# импортируем недостающее
from django.utils.text import slugify

# Create your models here.

# у товара будем видеть категории, имя, slug (для генерации url), 
# цвет, цена, desc (описание), фотографии, размер
# created/updated _at (когда был создан/обновлён)
class Category(models.Model): # встроенная функция в джанго, позволяющая формировать модели и задавать правильные поля для отправки в базу данных
  name = models.CharField(max_length=100) # CharField - поле для ввода текста
  slug = models.CharField(max_length=100,unique=True) # генерируем правильные url человекочитабельные. уникальные
  
  def save(self, *args, **kwargs):
    if not self.slug: # если в админке вручную не прописали slug
      self.slug =  slugify(self.name)
    super().save(*args, **kwargs) # сохраняем нашу категорию
      
  def __str__(self): # то, как оно будет отображаться в админке
    return self.name # хотим в url-пути .../catalog/tshirts/{name} видеть норм name


class Size(models.Model):
  name = models.CharField(max_length=20) # L, M, S, XXL и тд.
  
  def __str__(self):
    return self.name


class Product(models.Model):
  name = models.CharField(max_length=100)
  slug = models.CharField(max_length=100, unique=True)
  category = models.ForeignKey(Category,  # ForeignKey позволяет наследовать други модели, которые у нас уже есть. Получает те же самые поля, что в классе Category
                                on_delete=models.CASCADE, # on_delete отечает за то, что произойдёт при удалении. Если удалим категорию с товарами, то удаляем все продукты, которые есть в этой категории
                                related_name='products') 
  color = models.CharField(max_length=100) # название цвета
  price = models.DecimalField(max_digits=10, # с децимал полем можно адекватно считать скидки на товары
                              decimal_places=2) # 
  description = models.TextField(blank=True) # бланк тру - поле может быть пустым при заполнении в админке джанго
  main_image = models.ImageField(upload_to='products/main/') # куда будем сохранять фотки. При добавлении через админку фото сначала поместятся в папку media, потом в products
  created_at = models.DateTimeField(auto_now_add=True) # при автоматическом добавлении товара будет время само добавляться в бд
  updated_at = models.DateTimeField(auto_now_add=True) # при автоматическом обновлении товара будет время само добавляться в бд
  
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name


class ProductSize(models.Model): # хотим к товару привязать размер - L, M, S, XXL и тд. Количество товара на размер и доступность. Например у нас на складе только 10 размеров M
  product = models.ForeignKey(Product, 
                              on_delete=models.CASCADE,
                              related_name='product_size')
  size = models.ForeignKey(Size, 
                            on_delete=models.CASCADE,)
  stock = models.PositiveIntegerField(default=0) # доступное количество, которое люди могут купить
  
  def __str__(self):
    return f"{self.size.name} ({self.stock} in stock) for {self.product.name}" # В админке будет показываться, например: M (3 in stock) for Футболка чёрная


# тут соединяем продукт с его изображениями
# в каталоге будем показывать только main/image, при переходе на страницу товара будем показывать остальные его фотки с листанием и прочее. Это product image
class ProductImage(models.Model):
  product = models.ForeignKey(Product, 
                              on_delete=models.CASCADE,
                              related_name='images')
  image = models.ImageField(upload_to='products/extra/') # теперь будем загружать не в products/main, а в products/extra


