# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Challenge'
        db.create_table('challenge_challenge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='0', max_length=2)),
            ('is_contact_person', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('contact_person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contact_chl_set', to=orm['auth.User'])),
            ('is_alt_person', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('alt_person_fullname', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('alt_person_email', self.gf('django.db.models.fields.EmailField')(max_length=80, null=True, blank=True)),
            ('alt_person_phone', self.gf('django.db.models.fields.CharField')(default='', max_length=15, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['organization.Organization'], null=True, blank=True)),
            ('application', self.gf('django.db.models.fields.CharField')(default='0', max_length=2)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deleted_reason', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('challenge', ['Challenge'])

        # Adding model 'Participation'
        db.create_table('challenge_participation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('challenge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenge.Challenge'])),
            ('application_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('cancellation_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('selfreflection_activity_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('selfreflection_learning_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('selfreflection_rejection_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('acknowledgement_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='0', max_length=2)),
            ('date_created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('date_accepted', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_cancelled', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_selfreflection', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_selfreflection_rejection', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_acknowledged', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('share_on_FB', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('challenge', ['Participation'])

        # Adding model 'Comment'
        db.create_table('challenge_comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('challenge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenge.Challenge'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('challenge', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'Challenge'
        db.delete_table('challenge_challenge')

        # Deleting model 'Participation'
        db.delete_table('challenge_participation')

        # Deleting model 'Comment'
        db.delete_table('challenge_comment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'challenge.challenge': {
            'Meta': {'ordering': "['name']", 'object_name': 'Challenge'},
            'alt_person_email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'alt_person_fullname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'alt_person_phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'application': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '2'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'contact_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact_chl_set'", 'to': "orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted_reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_alt_person': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_contact_person': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['organization.Organization']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'start_time': ('django.db.models.fields.TimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '2'})
        },
        'challenge.comment': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'Comment'},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['challenge.Challenge']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'challenge.participation': {
            'Meta': {'ordering': "['date_created']", 'object_name': 'Participation'},
            'acknowledgement_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'application_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cancellation_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['challenge.Challenge']"}),
            'date_accepted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_acknowledged': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_cancelled': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_selfreflection': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_selfreflection_rejection': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selfreflection_activity_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'selfreflection_learning_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'selfreflection_rejection_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'share_on_FB': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'organization.organization': {
            'Meta': {'ordering': "['name']", 'object_name': 'Organization'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'affiliated_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'alt_person_email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'alt_person_fullname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'alt_person_phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact_org_set'", 'to': "orm['auth.User']"}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_alt_person': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_contact_person': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'postal_code': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['challenge']