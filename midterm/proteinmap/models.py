from django.db import models

class Organism(models.Model):
    taxa_id = models.IntegerField(primary_key=True, blank=False)
    clade = models.CharField(max_length=2, null=False, blank=False)
    genus = models.CharField(max_length=50, null=False, blank=False)
    species = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.genus + ' ' + self.species

class Protein(models.Model):
    protein_id = models.CharField(primary_key=True, max_length=12, blank=False)
    length = models.IntegerField(null=False, blank=False)
    organism = models.ForeignKey(Organism, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.protein_id

class Sequence(models.Model):
    protein = models.OneToOneField(Protein, on_delete=models.CASCADE, primary_key=True, related_name='sequence')
    sequence = models.TextField(max_length=40000, null=False, blank=True)

    def __str__(self):
        return self.sequence

class Pfam(models.Model):
    pfam_id = models.CharField(primary_key=True, max_length=20, blank=False)
    description = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.pfam_id

class Domain(models.Model):
    protein = models.ForeignKey(Protein, on_delete=models.CASCADE, related_name='domains')
    pfam = models.ForeignKey(Pfam, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=False, blank=False)
    start = models.IntegerField(null=False, blank=False)
    stop = models.IntegerField(null=False, blank=False)
