from django.urls import path
from . import views

urlpatterns = [
  # path('/<str:board_id>', views.BoardView.as_view(), name='board'),
  path('create-board/', views.CreateBoardView.as_view(), name='create-board'),
  path('get-boards/', views.GetBoardsView.as_view(), name='get-boards'),
  path('update-board/', views.UpdateBoardView.as_view(), name='update-board'),
  path('get-board-info/<str:board_slug>', views.GetBoardInfoView.as_view(), name='get-board-info'),
  # path('add-list/', views.CreateListView.as_view(), name='add-list'),
  # path('list/<str:list_id>', views.ListView.as_view(), name='list'),
]