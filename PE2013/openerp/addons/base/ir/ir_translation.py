# -*- coding: utf-8 -*-
##############################################################################
#
#    PengERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

TRANSLATION_TYPE = [
    ('field', 'Field'),
    ('model', 'Object'),
    ('rml', 'RML  (deprecated - use Report)'), # Pending deprecation - to be replaced by report!
    ('report', 'Report/Template'),
    ('selection', 'Selection'),
    ('view', 'View'),
    ('wizard_button', 'Wizard Button'),
    ('wizard_field', 'Wizard Field'),
    ('wizard_view', 'Wizard View'),
    ('xsl', 'XSL'),
    ('help', 'Help'),
    ('code', 'Code'),
    ('constraint', 'Constraint'),
    ('sql_constraint', 'SQL Constraint')
]

class ir_translation_import_cursor(object):
    """Temporary cursor for optimizing mass insert into ir.translation

    Open it (attached to a sql cursor), feed it with translation data and
    finish() it in order to insert multiple translations in a batch.
    """
    _table_name = 'tmp_ir_translation_import'

    def __init__(self, cr, uid, parent, context):
        """ Initializer

        Store some values, and also create a temporary SQL table to accept
        the data.
        @param parent an instance of ir.translation ORM model
        """
        self._cr = cr
        self._uid = uid
        self._context = context
        self._overwrite = context.get('overwrite', False)
        self._debug = False
        self._parent_table = parent._table

        # Note that Postgres will NOT inherit the constraints or indexes
        # of ir_translation, so this copy will be much faster.
        cr.execute('''CREATE TEMP TABLE %s(
            imd_model VARCHAR(64),
            imd_name VARCHAR(128)
            ) INHERITS (%s) ''' % (self._table_name, self._parent_table))

    def push(self, trans_dict):
        """Feed a translation, as a dictionary, into the cursor
        """
        params = dict(trans_dict, state="translated" if trans_dict['value'] else "to_translate")
        self._cr.execute("""INSERT INTO %s (name, lang, res_id, src, type, imd_model, module, imd_name, value, state, comments)
                            VALUES (%%(name)s, %%(lang)s, %%(res_id)s, %%(src)s, %%(type)s, %%(imd_model)s, %%(module)s,
                                    %%(imd_name)s, %%(value)s, %%(state)s, %%(comments)s)""" % self._table_name,
                         params)

    def finish(self):
        """ Transfer the data from the temp table to ir.translation
        """
        cr = self._cr
        if self._debug:
            cr.execute("SELECT count(*) FROM %s" % self._table_name)
            c = cr.fetchone()[0]
            _logger.debug("ir.translation.cursor: We have %d entries to process", c)

        # Step 1: resolve ir.model.data references to res_ids
        cr.execute("""UPDATE %s AS ti
            SET res_id = imd.res_id
            FROM ir_model_data AS imd
            WHERE ti.res_id IS NULL
                AND ti.module IS NOT NULL AND ti.imd_name IS NOT NULL

                AND ti.module = imd.module AND ti.imd_name = imd.name
                AND ti.imd_model = imd.model; """ % self._table_name)

        if self._debug:
            cr.execute("SELECT module, imd_model, imd_name FROM %s " \
                "WHERE res_id IS NULL AND module IS NOT NULL" % self._table_name)
            for row in cr.fetchall():
                _logger.debug("ir.translation.cursor: missing res_id for %s. %s/%s ", *row)

        # Records w/o res_id must _not_ be inserted into our db, because they are
        # referencing non-existent data.
        cr.execute("DELETE FROM %s WHERE res_id IS NULL AND module IS NOT NULL" % \
            self._table_name)

        find_expr = "irt.lang = ti.lang AND irt.type = ti.type " \
                    " AND irt.name = ti.name AND irt.src = ti.src " \
                    " AND (ti.type != 'model' OR ti.res_id = irt.res_id) "

        # Step 2: update existing (matching) translations
        if self._overwrite:
            cr.execute("""UPDATE ONLY %s AS irt
                SET value = ti.value,
                state = 'translated'
                FROM %s AS ti
                WHERE %s AND ti.value IS NOT NULL AND ti.value != ''
                """ % (self._parent_table, self._table_name, find_expr))

        # Step 3: insert new translations
        cr.execute("""INSERT INTO %s(name, lang, res_id, src, type, value, module, state, comments)
            SELECT name, lang, res_id, src, type, value, module, state, comments
              FROM %s AS ti
              WHERE NOT EXISTS(SELECT 1 FROM ONLY %s AS irt WHERE %s);
              """ % (self._parent_table, self._table_name, self._parent_table, find_expr))

        if self._debug:
            cr.execute('SELECT COUNT(*) FROM ONLY %s' % self._parent_table)
            c1 = cr.fetchone()[0]
            cr.execute('SELECT COUNT(*) FROM ONLY %s AS irt, %s AS ti WHERE %s' % \
                (self._parent_table, self._table_name, find_expr))
            c = cr.fetchone()[0]
            _logger.debug("ir.translation.cursor:  %d entries now in ir.translation, %d common entries with tmp", c1, c)

        # Step 4: cleanup
        cr.execute("DROP TABLE %s" % self._table_name)
        return True

class ir_translation(osv.osv):
    _name = "ir.translation"
    _log_access = False

    def _get_language(self, cr, uid, context):
        lang_model = self.pool.get('res.lang')
        lang_ids = lang_model.search(cr, uid, [('translatable', '=', True)], context=context)
        lang_data = lang_model.read(cr, uid, lang_ids, ['code', 'name'], context=context)
        return [(d['code'], d['name']) for d in lang_data]

    _columns = {
        'name': fields.char('Translated field', required=True),
        'res_id': fields.integer('Record ID', select=True),
        'lang': fields.selection(_get_language, string='Language'),
        'type': fields.selection(TRANSLATION_TYPE, string='Type', select=True),
        'src': fields.text('Source'),
        'value': fields.text('Translation Value'),
        'module': fields.char('Module', help="Module this term belongs to", select=True),

        'state': fields.selection(
            [('to_translate','To Translate'),
             ('inprogress','Translation in Progress'),
             ('translated','Translated')],
            string="Status",
            help="Automatically set to let administators find new terms that might need to be translated"),

        # aka gettext extracted-comments - we use them to flag openerp-web translation
        # cfr: http://www.gnu.org/savannah-checkouts/gnu/gettext/manual/html_node/PO-Files.html
        'comments': fields.text('Translation comments', select=True),
    }

    _defaults = {
        'state': 'to_translate',
    }

    _sql_constraints = [ ('lang_fkey_res_lang', 'FOREIGN KEY(lang) REFERENCES res_lang(code)',
        'Language code of translation item must be among known languages' ), ]

    def _auto_init(self, cr, context=None):
        super(ir_translation, self)._auto_init(cr, context)

        # FIXME: there is a size limit on btree indexed values so we can't index src column with normal btree.
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('ir_translation_ltns',))
        if cr.fetchone():
            #temporarily removed: cr.execute('CREATE INDEX ir_translation_ltns ON ir_translation (name, lang, type, src)')
            cr.execute('DROP INDEX ir_translation_ltns')
            cr.commit()
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('ir_translation_lts',))
        if cr.fetchone():
            #temporarily removed: cr.execute('CREATE INDEX ir_translation_lts ON ir_translation (lang, type, src)')
            cr.execute('DROP INDEX ir_translation_lts')
            cr.commit()

        # add separate hash index on src (no size limit on values), as postgres 8.1+ is able to combine separate indexes
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('ir_translation_src_hash_idx',))
        if not cr.fetchone():
            cr.execute('CREATE INDEX ir_translation_src_hash_idx ON ir_translation using hash (src)')

        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('ir_translation_ltn',))
        if not cr.fetchone():
            cr.execute('CREATE INDEX ir_translation_ltn ON ir_translation (name, lang, type)')
            cr.commit()

    def _check_selection_field_value(self, cr, uid, field, value, context=None):
        if field == 'lang':
            return
        return super(ir_translation, self)._check_selection_field_value(cr, uid, field, value, context=context)

    @tools.ormcache_multi(skiparg=3, multi=6)
    def _get_ids(self, cr, uid, name, tt, lang, ids):
        translations = dict.fromkeys(ids, False)
        if ids:
            cr.execute('select res_id,value '
                    'from ir_translation '
                    'where lang=%s '
                        'and type=%s '
                        'and name=%s '
                        'and res_id IN %s',
                    (lang,tt,name,tuple(ids)))
            for res_id, value in cr.fetchall():
                translations[res_id] = value
        return translations

    def _set_ids(self, cr, uid, name, tt, lang, ids, value, src=None):
        # clear the caches
        tr = self._get_ids(cr, uid, name, tt, lang, ids)
        for res_id in tr:
            if tr[res_id]:
                self._get_source.clear_cache(self, uid, name, tt, lang, tr[res_id])
            self._get_ids.clear_cache(self, uid, name, tt, lang, res_id)
        self._get_source.clear_cache(self, uid, name, tt, lang)

        cr.execute('delete from ir_translation '
                'where lang=%s '
                    'and type=%s '
                    'and name=%s '
                    'and res_id IN %s',
                (lang,tt,name,tuple(ids),))
        for id in ids:
            self.create(cr, uid, {
                'lang':lang,
                'type':tt,
                'name':name,
                'res_id':id,
                'value':value,
                'src':src,
                })
        return len(ids)

    @tools.ormcache(skiparg=3)
    def _get_source(self, cr, uid, name, types, lang, source=None):
        """
        Returns the translation for the given combination of name, type, language
        and source. All values passed to this method should be unicode (not byte strings),
        especially ``source``.

        :param name: identification of the term to translate, such as field name (optional if source is passed)
        :param types: single string defining type of term to translate (see ``type`` field on ir.translation), or sequence of allowed types (strings)
        :param lang: language code of the desired translation
        :param source: optional source term to translate (should be unicode)
        :rtype: unicode
        :return: the request translation, or an empty unicode string if no translation was
                 found and `source` was not passed
        """
        # FIXME: should assert that `source` is unicode and fix all callers to always pass unicode
        # so we can remove the string encoding/decoding.
        if not lang:
            return tools.ustr(source or '')
        if isinstance(types, basestring):
            types = (types,)
        if source:
            query = """SELECT value
                       FROM ir_translation
                       WHERE lang=%s
                        AND type in %s
                        AND src=%s"""
            params = (lang or '', types, tools.ustr(source))
            if name:
                query += " AND name=%s"
                params += (tools.ustr(name),)
            cr.execute(query, params)
        else:
            cr.execute("""SELECT value
                          FROM ir_translation
                          WHERE lang=%s
                           AND type in %s
                           AND name=%s""",
                    (lang or '', types, tools.ustr(name)))
        res = cr.fetchone()
        trad = res and res[0] or u''
        if source and not trad:
            return tools.ustr(source)
        return trad

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        ids = super(ir_translation, self).create(cr, uid, vals, context=context)
        self._get_source.clear_cache(self, uid, vals.get('name',0), vals.get('type',0),  vals.get('lang',0), vals.get('src',0))
        self._get_ids.clear_cache(self, uid, vals.get('name',0), vals.get('type',0), vals.get('lang',0), vals.get('res_id',0))
        return ids

    def write(self, cursor, user, ids, vals, context=None):
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if vals.get('src') or ('value' in vals and not(vals.get('value'))):
            vals.update({'state':'to_translate'})
        if vals.get('value'):
            vals.update({'state':'translated'})
        result = super(ir_translation, self).write(cursor, user, ids, vals, context=context)
        for trans_obj in self.read(cursor, user, ids, ['name','type','res_id','src','lang'], context=context):
            self._get_source.clear_cache(self, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], trans_obj['src'])
            self._get_ids.clear_cache(self, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], trans_obj['res_id'])
        return result

    def unlink(self, cursor, user, ids, context=None):
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        for trans_obj in self.read(cursor, user, ids, ['name','type','res_id','src','lang'], context=context):
            self._get_source.clear_cache(self, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], trans_obj['src'])
            self._get_ids.clear_cache(self, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], trans_obj['res_id'])
        result = super(ir_translation, self).unlink(cursor, user, ids, context=context)
        return result

    def translate_fields(self, cr, uid, model, id, field=None, context=None):
        trans_model = self.pool.get(model)
        domain = ['&', ('res_id', '=', id), ('name', '=like', model + ',%')]
        langs_ids = self.pool.get('res.lang').search(cr, uid, [('code', '!=', 'en_US')], context=context)
        if not langs_ids:
            raise osv.except_osv(_('Error'), _("Translation features are unavailable until you install an extra PengERP translation."))
        langs = [lg.code for lg in self.pool.get('res.lang').browse(cr, uid, langs_ids, context=context)]
        main_lang = 'en_US'
        translatable_fields = []
        for f, info in trans_model._all_columns.items():
            if info.column.translate:
                if info.parent_model:
                    parent_id = trans_model.read(cr, uid, [id], [info.parent_column], context=context)[0][info.parent_column][0]
                    translatable_fields.append({ 'name': f, 'id': parent_id, 'model': info.parent_model })
                    domain.insert(0, '|')
                    domain.extend(['&', ('res_id', '=', parent_id), ('name', '=', "%s,%s" % (info.parent_model, f))])
                else:
                    translatable_fields.append({ 'name': f, 'id': id, 'model': model })
        if len(langs):
            fields = [f.get('name') for f in translatable_fields]
            record = trans_model.read(cr, uid, [id], fields, context={ 'lang': main_lang })[0]
            for lg in langs:
                for f in translatable_fields:
                    # Check if record exists, else create it (at once)
                    sql = """INSERT INTO ir_translation (lang, src, name, type, res_id, value)
                        SELECT %s, %s, %s, 'model', %s, %s WHERE NOT EXISTS
                        (SELECT 1 FROM ir_translation WHERE lang=%s AND name=%s AND res_id=%s AND type='model');
                        UPDATE ir_translation SET src = %s WHERE lang=%s AND name=%s AND res_id=%s AND type='model';
                        """
                    src = record[f['name']] or None
                    name = "%s,%s" % (f['model'], f['name'])
                    cr.execute(sql, (lg, src , name, f['id'], src, lg, name, f['id'], src, lg, name, id))

        action = {
            'name': 'Translate',
            'res_model': 'ir.translation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
        }
        if field:
            info = trans_model._all_columns[field]
            action['context'] = {
                'search_default_name': "%s,%s" % (info.parent_model or model, field)
            }
        return action

    def _get_import_cursor(self, cr, uid, context=None):
        """ Return a cursor-like object for fast inserting translations
        """
        return ir_translation_import_cursor(cr, uid, self, context=context)

    def load(self, cr, modules, langs, context=None):
        context = dict(context or {}) # local copy
        for module_name in modules:
            modpath = openerp.modules.get_module_path(module_name)
            if not modpath:
                continue
            for lang in langs:
                lang_code = tools.get_iso_codes(lang)
                base_lang_code = None
                if '_' in lang_code:
                    base_lang_code = lang_code.split('_')[0]

                # Step 1: for sub-languages, load base language first (e.g. es_CL.po is loaded over es.po)
                if base_lang_code:
                    base_trans_file = openerp.modules.get_module_resource(module_name, 'i18n', base_lang_code + '.po')
                    if base_trans_file:
                        _logger.info('module %s: loading base translation file %s for language %s', module_name, base_lang_code, lang)
                        tools.trans_load(cr, base_trans_file, lang, verbose=False, module_name=module_name, context=context)
                        context['overwrite'] = True # make sure the requested translation will override the base terms later

                # Step 2: then load the main translation file, possibly overriding the terms coming from the base language
                trans_file = openerp.modules.get_module_resource(module_name, 'i18n', lang_code + '.po')
                if trans_file:
                    _logger.info('module %s: loading translation file (%s) for language %s', module_name, lang_code, lang)
                    tools.trans_load(cr, trans_file, lang, verbose=False, module_name=module_name, context=context)
                elif lang_code != 'en_US':
                    _logger.warning('module %s: no translation for language %s', module_name, lang_code)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
