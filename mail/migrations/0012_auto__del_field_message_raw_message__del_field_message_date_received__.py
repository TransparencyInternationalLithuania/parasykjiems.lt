# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Message.raw_message'
        db.delete_column('mail_message', 'raw_message')

        # Deleting field 'Message.date_received'
        db.delete_column('mail_message', 'date_received')

        # Adding field 'Message.date'
        db.add_column('mail_message', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2011, 10, 15, 11, 22, 55, 317670), blank=True), keep_default=False)

        # Adding field 'Message.envelope'
        db.add_column('mail_message', 'envelope', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'Message.sender_name'
        db.add_column('mail_message', 'sender_name', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Message.sender_email'
        db.add_column('mail_message', 'sender_email', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Message.recipient_name'
        db.add_column('mail_message', 'recipient_name', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Message.recipient_email'
        db.add_column('mail_message', 'recipient_email', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Message.subject'
        db.add_column('mail_message', 'subject', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Message.body_text'
        db.add_column('mail_message', 'body_text', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Message.message_id'
        db.add_column('mail_message', 'message_id', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True), keep_default=False)

        # Deleting field 'UnconfirmedMessage.is_open'
        db.delete_column('mail_unconfirmedmessage', 'is_open')

        # Adding field 'UnconfirmedMessage.is_public'
        db.add_column('mail_unconfirmedmessage', 'is_public', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'Thread.is_open'
        db.delete_column('mail_thread', 'is_open')

        # Adding field 'Thread.is_public'
        db.add_column('mail_thread', 'is_public', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Message.raw_message'
        raise RuntimeError("Cannot reverse this migration. 'Message.raw_message' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Message.date_received'
        raise RuntimeError("Cannot reverse this migration. 'Message.date_received' and its values cannot be restored.")

        # Deleting field 'Message.date'
        db.delete_column('mail_message', 'date')

        # Deleting field 'Message.envelope'
        db.delete_column('mail_message', 'envelope')

        # Deleting field 'Message.sender_name'
        db.delete_column('mail_message', 'sender_name')

        # Deleting field 'Message.sender_email'
        db.delete_column('mail_message', 'sender_email')

        # Deleting field 'Message.recipient_name'
        db.delete_column('mail_message', 'recipient_name')

        # Deleting field 'Message.recipient_email'
        db.delete_column('mail_message', 'recipient_email')

        # Deleting field 'Message.subject'
        db.delete_column('mail_message', 'subject')

        # Deleting field 'Message.body_text'
        db.delete_column('mail_message', 'body_text')

        # Deleting field 'Message.message_id'
        db.delete_column('mail_message', 'message_id')

        # Adding field 'UnconfirmedMessage.is_open'
        db.add_column('mail_unconfirmedmessage', 'is_open', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'UnconfirmedMessage.is_public'
        db.delete_column('mail_unconfirmedmessage', 'is_public')

        # Adding field 'Thread.is_open'
        db.add_column('mail_thread', 'is_open', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'Thread.is_public'
        db.delete_column('mail_thread', 'is_public')


    models = {
        'mail.message': {
            'Meta': {'object_name': 'Message'},
            'body_text': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'envelope': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_replied_to': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Message']", 'null': 'True'}),
            'recipient_email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'recipient_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'reply_hash': ('django.db.models.fields.BigIntegerField', [], {'default': '7458442692', 'db_index': 'True', 'blank': 'True'}),
            'sender_email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sender_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Thread']", 'null': 'True'})
        },
        'mail.thread': {
            'Meta': {'object_name': 'Thread'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator_email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'creator_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'representative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Representative']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        'mail.unconfirmedmessage': {
            'Meta': {'object_name': 'UnconfirmedMessage'},
            'body_text': ('django.db.models.fields.TextField', [], {}),
            'confirm_hash': ('django.db.models.fields.BigIntegerField', [], {'default': '4678887214', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
