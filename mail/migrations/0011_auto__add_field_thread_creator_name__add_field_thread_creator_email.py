# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Thread.creator_name'
        db.add_column('mail_thread', 'creator_name', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Thread.creator_email'
        db.add_column('mail_thread', 'creator_email', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Thread.creator_name'
        db.delete_column('mail_thread', 'creator_name')

        # Deleting field 'Thread.creator_email'
        db.delete_column('mail_thread', 'creator_email')


    models = {
        'mail.message': {
            'Meta': {'object_name': 'Message'},
            'date_received': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_replied_to': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Message']", 'null': 'True'}),
            'raw_message': ('django.db.models.fields.TextField', [], {}),
            'reply_hash': ('django.db.models.fields.BigIntegerField', [], {'default': '4259777386', 'db_index': 'True', 'blank': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Thread']", 'null': 'True'})
        },
        'mail.thread': {
            'Meta': {'object_name': 'Thread'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator_email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'creator_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'representative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Representative']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        'mail.unconfirmedmessage': {
            'Meta': {'object_name': 'UnconfirmedMessage'},
            'body_text': ('django.db.models.fields.TextField', [], {}),
            'confirm_hash': ('django.db.models.fields.BigIntegerField', [], {'default': '5567214598', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'representative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Representative']", 'null': 'True', 'blank': 'True'}),
            'sender_email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'sender_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'submitted_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
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
        }
    }

    complete_apps = ['mail']
