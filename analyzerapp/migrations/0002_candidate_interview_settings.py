from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzerapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='interview_role',
            field=models.CharField(default='Frontend Developer', max_length=100),
        ),
        migrations.AddField(
            model_name='candidate',
            name='interview_duration',
            field=models.PositiveIntegerField(default=20),
        ),
        migrations.AddField(
            model_name='candidate',
            name='interview_question_count',
            field=models.PositiveIntegerField(default=15),
        ),
    ]
