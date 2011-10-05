# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Article', fields ['location']
        db.create_index('web_article', ['location'])

        # Adding unique constraint on 'Article', fields ['location']
        db.create_unique('web_article', ['location'])

        # Adding index on 'Message', fields ['name']
        db.create_index('web_message', ['name'])

        # Adding unique constraint on 'Message', fields ['name']
        db.create_unique('web_message', ['name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Message', fields ['name']
        db.delete_unique('web_message', ['name'])

        # Removing index on 'Message', fields ['name']
        db.delete_index('web_message', ['name'])

        # Removing unique constraint on 'Article', fields ['location']
        db.delete_unique('web_article', ['location'])

        # Removing index on 'Article', fields ['location']
        db.delete_index('web_article', ['location'])


    models = {
        'web.article': {
            'Meta': {'object_name': 'Article'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'web.message': {
            'Meta': {'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300', 'db_index': 'True'})
        }
    }

    complete_apps = ['web']
