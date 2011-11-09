# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Institution.other_info'
        db.add_column('search_institution', 'other_info', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Institution.other_info'
        db.delete_column('search_institution', 'other_info')


    models = {
        'search.institution': {
            'Meta': {'object_name': 'Institution'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.InstitutionKind']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'other_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'})
        },
        'search.institutionkind': {
            'Meta': {'ordering': "['ordinal', 'name']", 'object_name': 'InstitutionKind'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {})
        },
        'search.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'elderate': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'})
        },
        'search.representative': {
            'Meta': {'unique_together': "(('institution', 'name', 'kind'),)", 'object_name': 'Representative'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']"}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.RepresentativeKind']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'other_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'})
        },
        'search.representativekind': {
            'Meta': {'ordering': "['ordinal', 'name']", 'object_name': 'RepresentativeKind'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {})
        },
        'search.territory': {
            'Meta': {'unique_together': "(('institution', 'municipality', 'elderate', 'city', 'street'),)", 'object_name': 'Territory'},
            'city': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'elderate': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']"}),
            'municipality': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'numbers': ('django.db.models.fields.TextField', [], {}),
            'street': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['search']
