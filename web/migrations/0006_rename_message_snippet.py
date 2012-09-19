# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('web_message', 'web_snippet')


    def backwards(self, orm):
        db.rename_table('web_snippet', 'web_message')


    models = {
        'web.article': {
            'Meta': {'object_name': 'Article'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'body_rendered': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'web.snippet': {
            'Meta': {'object_name': 'Snippet'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'body_rendered': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300', 'db_index': 'True'})
        }
    }

    complete_apps = ['web']
