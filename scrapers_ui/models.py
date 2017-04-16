from django.db import models

class Pho(models.Model):
    name = models.CharField(max_length=30)
    module = models.CharField(max_length=30)
    last_run = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class Logs(models.Model):
    source_id = models.ForeignKey(Pho, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    scraped = models.TextField()
    errors = models.TextField()
    warnings = models.TextField()

    def __str__(self):
        return self.date