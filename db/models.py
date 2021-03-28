from django.db import models


#class Category(models.Model):
#    parent = models.ForeignKey('Category', null=True, on_delete=models.PROTECT)
#    name = models.CharField(max_length=100)

class StockItem(models.Model):
    # TODO: Barcodes must be unique
    barcode = models.CharField(max_length=50, blank=False, null=False)
    # TODO: Name must not be ''
    name = models.CharField(max_length=100, blank=False, null=False)
    brand = models.CharField(max_length=100, blank=True, null=False)
    notes = models.TextField()
#    category = models.ForeignKey(Category, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.name}'

class LevelChange(models.Model):
    item = models.ForeignKey(StockItem, null=False, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    change = models.IntegerField()

