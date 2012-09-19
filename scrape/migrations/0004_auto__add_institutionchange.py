# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'InstitutionChange'
        db.create_table('scrape_institutionchange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True)),
            ('other_info', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True)),
        ))
        db.send_create_signal('scrape', ['InstitutionChange'])


    def backwards(self, orm):
        
        # Deleting model 'InstitutionChange'
        db.delete_table('scrape_institutionchange')


    models = {
        'scrape.institutionchange': {
            'Meta': {'object_name': 'InstitutionChange'},
            'email': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'other_info': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'})
        },
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
