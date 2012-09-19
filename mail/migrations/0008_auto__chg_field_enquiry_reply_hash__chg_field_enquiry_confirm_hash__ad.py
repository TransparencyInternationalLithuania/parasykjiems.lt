# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Enquiry.reply_hash'
        db.alter_column('mail_enquiry', 'reply_hash', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Enquiry.confirm_hash'
        db.alter_column('mail_enquiry', 'confirm_hash', self.gf('django.db.models.fields.IntegerField')())

        # Adding field 'Response.sent_reply_notification'
        db.add_column('mail_response', 'sent_reply_notification', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Changing field 'Enquiry.reply_hash'
        db.alter_column('mail_enquiry', 'reply_hash', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Enquiry.confirm_hash'
        db.alter_column('mail_enquiry', 'confirm_hash', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Deleting field 'Response.sent_reply_notification'
        db.delete_column('mail_response', 'sent_reply_notification')


    models = {
        'mail.enquiry': {
            'Meta': {'object_name': 'Enquiry'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'confirm_hash': ('django.db.models.fields.IntegerField', [], {'default': '188631', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Response']", 'null': 'True', 'blank': 'True'}),
            'recipient_email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'recipient_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'reply_hash': ('django.db.models.fields.IntegerField', [], {'default': '242964', 'db_index': 'True', 'blank': 'True'}),
            'representative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Representative']", 'null': 'True', 'blank': 'True'}),
            'sender_email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'sender_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'submitted_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'mail.response': {
            'Meta': {'object_name': 'Response'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Enquiry']", 'null': 'True'}),
            'raw_message': ('django.db.models.fields.TextField', [], {}),
            'received_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sent_reply_notification': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
