from django.shortcuts import get_object_or_404

from django.views.generic import  TemplateView, DetailView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import Category, Product, Size
from django.db.models import Q
# Create your views here.



# главная страница, которая будет появляться при заходе на сайт
class IndexView(TemplateView):
  template_name = 'main/base.html' # наша база, где есть блок контент, который мы будем менять
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['categories'] = Category.objects.all()
    context['current_category'] = None # фильтрация каталога будет
    return context
  
  def get(self, request, *args, **kwargs):
    context = self.get_context_data(**kwargs)
    if request.headers.get('HX-Request'):
      return TemplateResponse(request, 'main/home_content.html', context)
    return TemplateResponse(request, self.template_name, context)



class CatalogView(TemplateView):
  template = 'main/base.html'
  
  # словарь слагов, которые отвечают за сортировку
  FILTER_MAPPING = {
    'color' : lambda queryset, # кверисет - массив с продуктами
    value : queryset.filter(color__iexact=value), # вэлью в конце - это то, что выбрал человек в сортировке
    
    'min_price' : lambda queryset, # кверисет - массив с продуктами
    value : queryset.filter(price__gte=value), # вэлью в конце - это то, что выбрал человек в сортировке
    
    'max_price' : lambda queryset, # кверисет - массив с продуктами
    value : queryset.filter(price_gte=value), # вэлью в конце - это то, что выбрал человек в сортировке
    
    'size' : lambda queryset, # кверисет - массив с продуктами
    value : queryset.filter(product_size__size=value) # вэлью в конце - это то, что выбрал человек в сортировке
  }
  
  # Достаём из БД те элементы, с которыми будем взаимодействовать
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    category_slug = kwargs.get('category_slug')
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-created_at')
    current_category = None
    
    if category_slug:
      current_category = get_object_or_404(Category, slug=category_slug)
      products = products.filter(category=current_category)
    
    # поиск
    query = self.request.GET.get('q')
    if query:
      products = products.filter(
        Q(name_icontains=query) | Q(description_icontains=query)
        # поиск по названию товара | по описанию
      )
    
    filter_params = {}
    for param, filter_func in self.FILTER_MAPPING.items():
      value = self.request.GET.get(param)
      if value: # есть фильтрация от пользователя
        products = filter_func(products, value)
        filter_params[param] = value
      else: # нет фильтрации и фильтр пустой
        filter_params[param] = ''
    
    filter_params['q'] = query or ''
    context.update({         # в контексте храним те переменные, которые будем выводить
      'categories' : categories,
      'products' : products,
      'current_category' : category_slug,
      'filter_params' : filter_params,
      'sizes' : Size.objects.all(), # добавляем в контекст процессора размеры
      'search_query' : query or ''
    })
    
    if self.request.GET.get('show_search') == 'true': # отделение поиска от обычного каталога
      context['show_search'] = True
    elif self.request.GET.get('reset_search') == 'true':
      context['reset_search'] = True
    
    return context
  
  
  def get(self, request, *args, **kwargs):
    context = self.get_context_data(**kwargs)
    if request.headers.get('HX-Request'):
      if context.get('show_search'):
        return TemplateResponse(request, 'main/search_input.html', context) # ответ в виде шаблона. search_input - шаблон, где можно ввести текст по которому мы хотим осуществлять поиск
      elif context.get('reset_search'):
        return TemplateResponse(request, 'main/search_button.html', {})
      template = 'main/filter_modal.html' if request.GET.get('show_filters') == True else 'main/catalog.html'
      return TemplateResponse(request, template, context)
    return TemplateResponse(request, self.template_name, context)


class ProductDetailView(DetailView):
  model = Product
  template_name = 'main/base.html'
  slug_field = 'slug'
  slug_url_kwarg = 'slug'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    product = self.get_object()
    context['categories'] = Category.objects.all()
    context['related_products'] = Product.objects.filter(
      category = product.category
    ).exclude(id=product.id)[:4]
    context['current_category'] = product.category.slug
    return context
  
  
  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    context = self.get_context_data(**kwargs)
    if request.headers.get('HX-Request'):
      return TemplateResponse(request, 'main/product_detail.html', context)
    raise TemplateResponse(request, self.template_name, context)
  
  
  pass
