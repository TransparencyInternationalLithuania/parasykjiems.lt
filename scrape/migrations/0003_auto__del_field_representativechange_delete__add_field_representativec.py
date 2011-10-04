# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'RepresentativeChange.delete'
        db.delete_column('scrape_representativechange', 'delete')

        # Adding field 'RepresentativeChange.delete_rep'
        db.add_column('scrape_representativechange', 'delete_rep', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'RepresentativeChange.delete'
        db.add_column('scrape_representativechange', 'delete', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'RepresentativeChange.delete_rep'
        db.delete_column('scrape_representativechange', 'delete_rep')


    models = {
        'scrape.representativechange': {
            'Meta': {'object_name': 'RepresentativeChange'},
            'delete_rep': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'kind_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'other_info': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'})
        }
    }

    complete_apps = ['scrape']
