import django_tables2 as tables
from .models import BudgetTracker

class BudgetTable(tables.Table):
    class Meta:
        model = BudgetTracker
        template_name = "django_tables2/bootstrap4.html"
        total_left = tables.Column()
        budget_amount = tables.Column()
        monthly_spend = tables.Column()
        fields = ("category", "budget_amount", "date", "monthly_spend", "total_left" )
    def render_total_left(self, value):
        return '${:0.2f}'.format(value)        
    def render_budget_amount(self, value):
        return '${:0.2f}'.format(value)    
    def render_monthly_spend(self, value):
        return '${:0.2f}'.format(value)              