# Generated by Django 4.0.4 on 2024-12-07 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asistente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('area', models.CharField(max_length=100)),
                ('celular', models.CharField(max_length=15)),
                ('correo', models.EmailField(max_length=254)),
                ('fecha_nacimiento', models.DateField()),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
            ],
        ),
        migrations.CreateModel(
            name='Catalogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duracion', models.PositiveIntegerField()),
                ('unidad_duracion', models.CharField(choices=[('Horas', 'Horas'), ('Días', 'Días')], max_length=5)),
                ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Cancelado', 'Cancelado')], default='Activo', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.TextField()),
                ('contacto', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('celular', models.CharField(max_length=15)),
                ('correo', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentarios', models.TextField()),
                ('puntuacion', models.PositiveIntegerField(default=0)),
                ('asistente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluaciones', to='core.asistente')),
            ],
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duracion', models.PositiveIntegerField()),
                ('unidad_duracion', models.CharField(choices=[('Horas', 'Horas'), ('Días', 'Días')], max_length=5)),
                ('inicio', models.DateField()),
                ('temario', models.TextField()),
                ('direccion', models.TextField()),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('notas', models.TextField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('En curso', 'En curso'), ('Terminado', 'Terminado')], default='En curso', max_length=15)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalogo', to='core.catalogo')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cursos', to='core.instructor')),
            ],
        ),
        migrations.AddField(
            model_name='asistente',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asistentes', to='core.curso'),
        ),
    ]
