# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Organization'
        db.create_table('organization_organization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('postal_code', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('country', self.gf('django_countries.fields.CountryField')(max_length=2)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('video', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('is_contact_person', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('contact_person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_alt_person', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('alt_person_fullname', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('alt_person_email', self.gf('django.db.models.fields.EmailField')(max_length=80, null=True, blank=True)),
            ('alt_person_phone', self.gf('django.db.models.fields.CharField')(default='', max_length=15, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('organization', ['Organization'])


    def backwards(self, orm):
        # Deleting model 'Organization'
        db.delete_table('organization_organization')


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
            'alt_person_email': ('django.db.models.fields.EmailField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'alt_person_fullname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'alt_person_phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_alt_person': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_contact_person': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'postal_code': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['organization']