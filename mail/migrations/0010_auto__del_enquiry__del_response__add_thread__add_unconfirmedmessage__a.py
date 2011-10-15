# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Enquiry'
        db.delete_table('mail_enquiry')

        # Deleting model 'Response'
        db.delete_table('mail_response')

        # Adding model 'Thread'
        db.create_table('mail_thread', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Institution'], null=True, blank=True)),
            ('representative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Representative'], null=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=400)),
        ))
        db.send_create_signal('mail', ['Thread'])

        # Adding model 'UnconfirmedMessage'
        db.create_table('mail_unconfirmedmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('confirm_hash', self.gf('django.db.models.fields.BigIntegerField')(default=7385282585, db_index=True, blank=True)),
            ('sender_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sender_email', self.gf('django.db.models.fields.EmailField')(max_length=200)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('body_text', self.gf('django.db.models.fields.TextField')()),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submitted_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Institution'], null=True, blank=True)),
            ('representative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Representative'], null=True, blank=True)),
        ))
        db.send_create_signal('mail', ['UnconfirmedMessage'])

        # Adding model 'Message'
        db.create_table('mail_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reply_hash', self.gf('django.db.models.fields.BigIntegerField')(default=7741236254, db_index=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mail.Message'], null=True)),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mail.Thread'], null=True)),
            ('date_received', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('raw_message', self.gf('django.db.models.fields.TextField')()),
            ('is_replied_to', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('mail', ['Message'])


    def backwards(self, orm):
        
        # Adding model 'Enquiry'
        db.create_table('mail_enquiry', (
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('django.db.models.fields.CharField')(blank=True, max_length=40, db_index=True)),
            ('representative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Representative'], null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mail.Response'], null=True, blank=True)),
            ('is_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sender_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('submitted_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Institution'], null=True, blank=True)),
            ('message_id', self.gf('django.db.models.fields.CharField')(blank=True, max_length=100, null=True, db_index=True)),
            ('is_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reply_hash', self.gf('django.db.models.fields.BigIntegerField')(default=2355464200, blank=True, db_index=True)),
            ('sender_email', self.gf('django.db.models.fields.EmailField')(max_length=200)),
            ('recipient_email', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('recipient_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('confirm_hash', self.gf('django.db.models.fields.BigIntegerField')(default=6959282987, blank=True, db_index=True)),
        ))
        db.send_create_signal('mail', ['Enquiry'])

        # Adding model 'Response'
        db.create_table('mail_response', (
            ('sent_reply_notification', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('received_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mail.Enquiry'], null=True)),
            ('raw_message', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('mail', ['Response'])

        # Deleting model 'Thread'
        db.delete_table('mail_thread')

        # Deleting model 'UnconfirmedMessage'
        db.delete_table('mail_unconfirmedmessage')

        # Deleting model 'Message'
        db.delete_table('mail_message')


    models = {
        'mail.message': {
            'Meta': {'object_name': 'Message'},
            'date_received': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_replied_to': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Message']", 'null': 'True'}),
            'raw_message': ('django.db.models.fields.TextField', [], {}),
            'reply_hash': ('django.db.models.fields.BigIntegerField', [], {'default': '3112588744', 'db_index': 'True', 'blank': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Thread']", 'null': 'True'})
        },
        'mail.thread': {
            'Meta': {'object_name': 'Thread'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
            'confirm_hash': ('django.db.models.fields.BigIntegerField', [], {'default': '9421771207', 'db_index': 'True', 'blank': 'True'}),
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
