# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'InstitutionChange.name'
        db.delete_column('scrape_institutionchange', 'name')

        # Adding field 'InstitutionChange.address'
        db.add_column('scrape_institutionchange', 'address', self.gf('django.db.models.fields.TextField')(default=None, null=True), keep_default=False)

        # Changing field 'InstitutionChange.other_info'
        db.alter_column('scrape_institutionchange', 'other_info', self.gf('django.db.models.fields.TextField')(null=True))

        # Deleting field 'RepresentativeChange.kind_name'
        db.delete_column('scrape_representativechange', 'kind_name')

        # Deleting field 'RepresentativeChange.institution'
        db.delete_column('scrape_representativechange', 'institution')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'InstitutionChange.name'
        raise RuntimeError("Cannot reverse this migration. 'InstitutionChange.name' and its values cannot be restored.")

        # Deleting field 'InstitutionChange.address'
        db.delete_column('scrape_institutionchange', 'address')

        # Changing field 'InstitutionChange.other_info'
        db.alter_column('scrape_institutionchange', 'other_info', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # User chose to not deal with backwards NULL issues for 'RepresentativeChange.kind_name'
        raise RuntimeError("Cannot reverse this migration. 'RepresentativeChange.kind_name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RepresentativeChange.institution'
        raise RuntimeError("Cannot reverse this migration. 'RepresentativeChange.institution' and its values cannot be restored.")


    models = {
        'scrape.institutionchange': {
            'Meta': {'object_name': 'InstitutionChange'},
            'address': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other_info': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'})
        },
        'scrape.representativechange': {
            'Meta': {'object_name': 'RepresentativeChange'},
            'delete_rep': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'other_info': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True'})
        }
    }

    complete_apps = ['scrape']
