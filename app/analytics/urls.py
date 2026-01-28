from django.urls import path
from .views import TickerListView, FinancialDataView, MarketSummaryView

urlpatterns = [
    path('tickers/', TickerListView.as_view(), name='ticker-list'),
    path('data/<str:ticker>/', FinancialDataView.as_view(), name='financial-data'),
    path('summary/', MarketSummaryView.as_view(), name='market-summary'),
]
