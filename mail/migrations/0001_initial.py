# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Enquiry'
        db.create_table('mail_enquiry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('confirm_hash', self.gf('django.db.models.fields.IntegerField')(unique=True, db_index=True)),
            ('reply_hash', self.gf('django.db.models.fields.IntegerField')(unique=True, db_index=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Institution'], null=True)),
            ('representative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Representative'], null=True)),
            ('sender_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sender_email', self.gf('django.db.models.fields.EmailField')(max_length=200)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submitted_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('message_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mail.Response'], null=True)),
        ))
        db.send_create_signal('mail', ['Enquiry'])

        # Adding model 'Response'
        db.create_table('mail_response', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mail.Enquiry'], null=True)),
            ('received_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('raw_message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('mail', ['Response'])


    def backwards(self, orm):
        
        # Deleting model 'Enquiry'
        db.delete_table('mail_enquiry')

        # Deleting model 'Response'
        db.delete_table('mail_response')


    models = {
        'mail.enquiry': {
            'Meta': {'object_name': 'Enquiry'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'confirm_hash': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']", 'null': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Response']", 'null': 'True'}),
            'reply_hash': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'representative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Representative']", 'null': 'True'}),
            'sender_email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'sender_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'submitted_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'mail.response': {
            'Meta': {'object_name': 'Response'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mail.Enquiry']", 'null': 'True'}),
            'raw_message': ('django.db.models.fields.TextField', [], {}),
            'received_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'search.institution': {
            'Meta': {'object_name': 'Institution'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.InstitutionKind']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'search.institutionkind': {
            'Meta': {'object_name': 'InstitutionKind'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'search.representative': {
            'Meta': {'object_name': 'Representative'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Institution']"}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.RepresentativeKind']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'other_contacts': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'search.representativekind': {
            'Meta': {'object_name': 'RepresentativeKind'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['mail']
