# -*- coding: utf-8 -*-
from ast import literal_eval
import base64
import csv
import itertools
from _sqlite3 import Row

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
from openerp import models, fields, api


HEADER = ['participant_id','pinfo_firstname','pinfo_lastname','pinfo_birthdate','participant_email','pinfo_address','pinfo_city_id','pinfo_postalcode','pinfo_locality','pinfo_phone_number','pinfo_mobile_number','participant_password','participant_language_id','participant_activated','participant_logged_on','participant_created_on','participant_updated_on','pinfo_title_id','pinfo_sex','pinfo_nationality_country_id','pinfo_number_children','pinfo_child0_birthyear','pinfo_child0_sex','pinfo_child1_birthyear','pinfo_child1_sex','pinfo_child2_birthyear','pinfo_child2_sex','pinfo_child3_birthyear','pinfo_child3_sex','pinfo_child4_birthyear','pinfo_child4_sex','pinfo_child5_birthyear','pinfo_child5_sex','pinfo_child6_birthyear','pinfo_child6_sex','pinfo_child7_birthyear','pinfo_child7_sex','pinfo_child8_birthyear','pinfo_child8_sex','pinfo_child9_birthyear','pinfo_child9_sex','pinfo_is_single','pinfo_is_cohabiting','pinfo_is_married','pinfo_is_divorced','pinfo_is_widow','pinfo_is_living_with_parents','pinfo_country_id','pinfo_mobile_operator','pinfo_education_level_id','pinfo_partner_education_level_id','pinfo_profession_looking_for','pinfo_profession_employee','pinfo_profession_worker','pinfo_profession_independent','pinfo_profession_student','pinfo_profession_housewife','pinfo_profession_retired','pinfo_profession_independent_comp','pinfo_profession_name','pinfo_profession_typeofbusiness','pinfo_works_bank_insurance_id','pinfo_works_administration_id','pinfo_works_telecom_id','pinfo_works_food_id','pinfo_works_computer_id','pinfo_works_big_distribution_id','pinfo_works_energy_id','pinfo_works_chemistry_id','pinfo_works_transportation_id','pinfo_works_pharmaceutical_id','pinfo_works_advertising_id','pinfo_knows_french','pinfo_knows_dutch','pinfo_knows_english','pinfo_knows_spanish','pinfo_knows_italian','pinfo_knows_german','pinfo_knows_arabic','pinfo_knows_eastern_language','pinfo_knows_nordic_language','pinfo_has_car','pinfo_car_brand','pinfo_car_model','pinfo_is_smoker','pinfo_tobacco_brand','pinfo_hypermarket','pinfo_buys_big_brand','pinfo_buys_sign_brand','pinfo_has_pet_cat','pinfo_has_pet_dog','pinfo_has_pet_other','pinfo_allow_brussels','pinfo_allow_namur','pinfo_allow_liege','pinfo_allow_mons','pinfo_allow_charleroi','pinfo_allow_gent','pinfo_allow_antwerpen','pinfo_allow_brugge','pinfo_regsrc_id','pinfo_availability']
CUSTOMER_HEADER = ['reference','name','addresse','zip_code','country_code','city','phone','fax','email','website','vat','contact','active']
GROUP_HEADER = ['ref_etude','sujet','ref_client','date_etude']
NOTE_HEADER = ['reference','date','note']
PARTICIPATION_HEADER = ['Etude','Ref Recolte']

HEADER_NORMAL = [
    'participant_id',
    'pinfo_firstname',
    'pinfo_lastname',
    'pinfo_birthdate',
    'participant_email',
    'pinfo_address',
    'pinfo_city_id',
    'pinfo_postalcode',
    'pinfo_locality',
    'pinfo_phone_number',
    'pinfo_mobile_number',
    'pinfo_sex',
    'participant_activated',
    'participant_updated_on',
    'pinfo_number_children',
    'pinfo_child0_birthyear',
    'pinfo_child0_sex',
    'pinfo_child1_birthyear',
    'pinfo_child1_sex',
    'pinfo_child2_birthyear',
    'pinfo_child2_sex',
    'pinfo_child3_birthyear',
    'pinfo_child3_sex',
    'pinfo_child4_birthyear',
    'pinfo_child4_sex',
    'pinfo_child5_birthyear',
    'pinfo_child5_sex',
    'pinfo_child6_birthyear',
    'pinfo_child6_sex',
    'pinfo_child7_birthyear',
    'pinfo_child7_sex',
    'pinfo_child8_birthyear',
    'pinfo_child8_sex',
    'pinfo_child9_birthyear',
    'pinfo_child9_sex',
    'pinfo_mobile_operator',
    'pinfo_profession_name',
    'pinfo_profession_typeofbusiness',
    'pinfo_car_brand',
    'pinfo_car_model',
    'pinfo_tobacco_brand',
    'pinfo_hypermarket',
    'pinfo_buys_big_brand',
    'pinfo_buys_sign_brand']

HEADER_SPECIAL_PARSE = [
    'participant_id',
    'participant_language_id',
    'pinfo_title_id',
    'pinfo_availability',
    'pinfo_education_level_id',
    'pinfo_partner_education_level_id']

HEADER_PROFESSION = [
    'pinfo_profession_looking_for',
    'pinfo_profession_employee',
    'pinfo_profession_worker',
    'pinfo_profession_independent',
    'pinfo_profession_student',
    'pinfo_profession_housewife',
    'pinfo_profession_retired',
    'pinfo_profession_independent_comp']

HEADER_WORKS = [
    'pinfo_works_bank_insurance_id',
    'pinfo_works_administration_id',
    'pinfo_works_telecom_id',
    'pinfo_works_food_id',
    'pinfo_works_computer_id',
    'pinfo_works_big_distribution_id',
    'pinfo_works_energy_id',
    'pinfo_works_chemistry_id',
    'pinfo_works_transportation_id',
    'pinfo_works_pharmaceutical_id',
    'pinfo_works_advertising_id']

HEADER_MARITAL_STATUS = [
    'pinfo_is_single',
    'pinfo_is_cohabiting',
    'pinfo_is_married',
    'pinfo_is_divorced',
    'pinfo_is_widow',
    'pinfo_is_living_with_parents']

HEADER_BOOLEAN = [
    'pinfo_knows_french',
    'pinfo_knows_dutch',
    'pinfo_knows_english',
    'pinfo_knows_spanish',
    'pinfo_knows_italian',
    'pinfo_knows_german',
    'pinfo_knows_arabic',
    'pinfo_knows_eastern_language',
    'pinfo_knows_nordic_language',
    'pinfo_has_car',
    'pinfo_is_smoker',
    'pinfo_has_pet_cat',
    'pinfo_has_pet_dog',
    'pinfo_has_pet_other',
    'pinfo_allow_brussels',
    'pinfo_allow_namur',
    'pinfo_allow_liege',
    'pinfo_allow_mons',
    'pinfo_allow_charleroi',
    'pinfo_allow_gent',
    'pinfo_allow_antwerpen',
    'pinfo_allow_brugge']

COUNTRY_FILE = {'1':'BE','3':'FR','4':'DE','5':'AT','6':'DK','7':'ES','8':'FI','9':'GR','10':'IE','11':'IT','12':'LU','13':'NL','14':'PT','15':'GB','16':'SE','17':'CH','18':'NO','19':'US','20':'CA','22':'BG','23':'HR','24':'EE','25':'FO','26':'IS','27':'LV','28':'LI','29':'LT','30':'MC','31':'PL','32':'RO','33':'SK','34':'CZ','35':'TR','36':'SI','37':'MX','38':'PT','39':'AF','40':'ZA','41':'AL','42':'DZ','43':'AD','44':'AO','45':'AI','46':'AG','47':'AN','48':'SA','49':'AR','50':'AM','51':'AW','52':'AU','53':'AZ','54':'BS','55':'BH','56':'BD','57':'BB','58':'BZ','59':'BJ','60':'BM','61':'BT','62':'BY','63':'GN','64':'BO','65':'BW','66':'BR','67':'BN','68':'BF','69':'BI','70':'KH','71':'CM','72':'CV','74':'CF','75':'CL','76':'CN','77':'CX','78':'CY','80':'CC','81':'CO','82':'KM','83':'CD','84':'CG','85':'CK','86':'KP','87':'KR','88':'CK','89':'CI','90':'CU','91':'IO','92':'DJ','93':'DM','94':'EG','95':'SV','96':'AE','97':'EC','98':'ER','99':'ET','100':'FK','101':'FJ','102':'GA','103':'GM','104':'GE','105':'GH','106':'GI','107':'GD','108':'GL','109':'GP','110':'GU','111':'US','112':'GT','113':'GW','114':'GQ','115':'GY','117':'HT','118':'HN','119':'HK','120':'HU','121':'KY','122':'VG','123':'VI','124':'IN','125':'ID','126':'IR','127':'IQ','128':'IL','129':'JM','130':'JP','131':'JO','133':'KZ','134':'KE','135':'KG','136':'KI','137':'KW','138':'LA','139':'LS','140':'LB','141':'LR','142':'LY','143':'MO','144':'MK','145':'MG','148':'MY','149':'MW','150':'MV','151':'ML','152':'MT','153':'MA','154':'MH','155':'MQ','156':'MU','157':'MR','158':'YT','159':'FM','160':'UM','161':'MD','162':'MN','163':'MS','164':'MZ','165':'MM','166':'NA','167':'NR','168':'NP','169':'NI','170':'NE','171':'NG','172':'NU','173':'NF','174':'NC','175':'NZ','176':'OM','177':'UG','178':'UZ','179':'PK','180':'PW','181':'PA','182':'PG','183':'PY','184':'PE','185':'PH','186':'PF','187':'PR','188':'QA','190':'DO','191':'RE','192':'RU','193':'RW','195':'KN','196':'SM','197':'VC','198':'MP','199':'SB','200':'AS','201':'WS','202':'ST','203':'SN','204':'SC','205':'SL','206':'SG','207':'SO','208':'SD','209':'LK','210':'SH','211':'LC','212':'SR','213':'SZ','214':'SY','215':'TJ','216':'TW','217':'TZ','218':'TD','219':'TH','220':'TG','221':'TO','223':'TT','224':'TN','225':'TM','226':'TC','227':'TV','228':'UA','229':'UY','231':'VU','232':'VE','233':'VN','234':'UM','235':'WF','236':'YE','237':'BA','238':'YU','239':'ZM','240':'ZW','241':'TP','242':'VA','243':'PS'}

LANGUAGE_FILE = {'1':'en_US','2':'fr_BE','3':'nl_BE'}

AVAILABILITY_FILE = {'1':'day','2':'evening','3':'both'}

TITLE_FILE = {'1':'Mr.','2':'Mrs.','3':'Miss'}

EDU_LEVEL_FILE = {'1':'1','2':'2','3':'6','4':'4','5':'5','6':'6'}

# field with value None are not imported
MAPPER = {
    'participant_id':'ref_number',
    'pinfo_firstname':'firstname',
    'pinfo_lastname':'lastname',
    'pinfo_birthdate':'birthdate',
    'participant_email':'email',
    'pinfo_address':'street',
    'pinfo_city_id':None,
    'pinfo_postalcode':'zip',
    'pinfo_locality':'city',
    'pinfo_phone_number':'phone',
    'pinfo_mobile_number':'mobile',
    'participant_password':None,
    'participant_language_id':None,
    'participant_activated':None,
    'participant_logged_on':None,
    'participant_created_on':'creation_date',
    'participant_updated_on':'profile_last_update',
    'pinfo_title_id':None,
    'pinfo_sex':'gender',
    'pinfo_nationality_country_id':'nationality_id',
    'pinfo_number_children':'numberofchildren',
    'pinfo_child0_birthyear':'child1_yearofbirth',
    'pinfo_child0_sex':'child1_gender',
    'pinfo_child1_birthyear':'child2_yearofbirth',
    'pinfo_child1_sex':'child2_gender',
    'pinfo_child2_birthyear':'child3_yearofbirth',
    'pinfo_child2_sex':'child3_gender',
    'pinfo_child3_birthyear':'child4_yearofbirth',
    'pinfo_child3_sex':'child4_gender',
    'pinfo_child4_birthyear':'child5_yearofbirth',
    'pinfo_child4_sex':'child5_gender',
    'pinfo_child5_birthyear':'child6_yearofbirth',
    'pinfo_child5_sex':'child6_gender',
    'pinfo_child6_birthyear':'child7_yearofbirth',
    'pinfo_child6_sex':'child7_gender',
    'pinfo_child7_birthyear':'child8_yearofbirth',
    'pinfo_child7_sex':'child8_gender',
    'pinfo_child8_birthyear':'child9_yearofbirth',
    'pinfo_child8_sex':'child9_gender',
    'pinfo_child9_birthyear':'child10_yearofbirth',
    'pinfo_child9_sex':'child10_gender',
    'pinfo_is_single':'single',
    'pinfo_is_cohabiting':'cohabiting',
    'pinfo_is_married':'married',
    'pinfo_is_divorced':'divorced',
    'pinfo_is_widow':'widowed',
    'pinfo_is_living_with_parents':'with_parents',
    'pinfo_country_id':'county_id',
    'pinfo_mobile_operator':'mobile_operator',
    'pinfo_education_level_id':'edu_level_id',
    'pinfo_partner_education_level_id':'partner_edu_level_id',
    'pinfo_profession_looking_for':'lookingfor',
    'pinfo_profession_employee':'employee',
    'pinfo_profession_worker':'worker',
    'pinfo_profession_independent':'independant',
    'pinfo_profession_student':'student',
    'pinfo_profession_housewife':'housewife',
    'pinfo_profession_retired':'retired',
    'pinfo_profession_independent_comp':'profession_indie_comp',
    'pinfo_profession_name':'profession_name',
    'pinfo_profession_typeofbusiness':None,
    'pinfo_works_bank_insurance_id':None,
    'pinfo_works_administration_id':None,
    'pinfo_works_telecom_id':None,
    'pinfo_works_food_id':None,
    'pinfo_works_computer_id':None,
    'pinfo_works_big_distribution_id':None,
    'pinfo_works_energy_id':None,
    'pinfo_works_chemistry_id':None,
    'pinfo_works_transportation_id':None,
    'pinfo_works_pharmaceutical_id':None,
    'pinfo_works_advertising_id':None,
    'pinfo_knows_french':'knows_french',
    'pinfo_knows_dutch':'knows_dutch',
    'pinfo_knows_english':'knows_english',
    'pinfo_knows_spanish':'knows_spanish',
    'pinfo_knows_italian':'knows_italian',
    'pinfo_knows_german':'knows_german',
    'pinfo_knows_arabic':'knows_arabic',
    'pinfo_knows_eastern_language':'knows_eastern',
    'pinfo_knows_nordic_language':'knows_nordic',
    'pinfo_has_car':'has_car',
    'pinfo_car_brand':'car_brand',
    'pinfo_car_model':'car_model',
    'pinfo_is_smoker':'is_smoker',
    'pinfo_tobacco_brand':'tobacco_brand',
    'pinfo_hypermarket':'hypermarket',
    'pinfo_buys_big_brand':'buys_big_brand',
    'pinfo_buys_sign_brand':'buys_sign_brand',
    'pinfo_has_pet_cat':'has_pet_cat',
    'pinfo_has_pet_dog':'has_pet_dog',
    'pinfo_has_pet_other':'has_pet_other',
    'pinfo_allow_brussels':'allow_brussels',
    'pinfo_allow_namur':'allow_namur',
    'pinfo_allow_liege':'allow_liege',
    'pinfo_allow_mons':'allow_mons',
    'pinfo_allow_charleroi':'allow_charleroi',
    'pinfo_allow_gent':'allow_gent',
    'pinfo_allow_antwerpen':'allow_antwerpen',
    'pinfo_allow_brugge':'allow_brugge',
    'pinfo_regsrc_id': None,
    'pinfo_availability':'availability'
    }

CUSTOMER_MAPPER = {
    'reference':'ref',
    'name':'lastname',
    'addresse':'street',
    'zip_code':'zip',
    'country_code':'country_id',
    'city':'city',
    'phone':'phone',
    'fax':'fax',
    'email':'email',
    'website':'website',
    'vat':None,
    'contact':'child_ids',
    'active':None,
    }

GROUP_MAPPER = {
    'ref_etude':'reference_number',
    'sujet':'name',
    'ref_client':'customer',
    'date_etude':'start_date'
    }

NOTE_MAPPER = {
    'reference':'partner_id',
    'date':'date',
    'note':'name'
    }

PARTICIPATION_MAPPER = {
    'Etude':'',
    'Ref Recolte':''
    }

class ImportRespondentsWizard(models.TransientModel):
    _name = 'import.respondent.wizard'
    
    file = fields.Binary(string="Import csv file", help='Load the csv file containing the respondent you want to load in the system')
    filename = fields.Char(string="Filename")
    type = fields.Selection([('count','Count lines'),
                             ('missing','Missing rows'),
                             ('update_group_customer','Update group'),
                             ('customer','Customer'),
                             ('bad_sab','Respondent BAD/SAB'),
                             ('respondent','Respondent'),
                             ('group','Group'),
                             ('participation','Participation'),
                             ('lang_and_so','Languages and other things'),
                             ('notes','notes')],string="Type of import")
    
    def get_language_dict(self):
        languages = {}
        for lang in self.env['res.lang'].search([]):
            languages[lang.code] = lang.id 
        return languages
        
    def get_country_dict(self):
        countries = {}
        for country in self.env['res.country'].search([]):
            countries[country.code] = country.id 
        return countries
    
    def get_customer_dict(self):
        customers = {}
        for customer in self.env['res.partner'].search([('is_company','=',True),('customer','=',True),('is_respondent','=',False)]):
            customers[customer.ref] = customer.id
        
        return customers
    
    def get_respondent_dict(self):
        respondents = {}
        res = self.env['res.partner'].search_read([('is_respondent','=',True)],[('ref_number')])
        for respondent in res:
            respondents[respondent['ref_number']] = respondent['id']
        
        return respondents
    
    def get_group_dict(self):
        groups = {}
        res = self.env['event.event'].search_read([],[('reference_number')])
        for group in res:
            groups[group['reference_number']] = group['id']
        
        return groups
    
    def get_title_dict(self):
        titles = {}
        for title in self.env['res.partner.title'].search([]):
            titles[title.shortcut] = title.id 
        return titles
    
    def get_edu_level_dict(self):
        edu_levels = {}
        for edu_level in self.env['res.partner.education.level'].search([]):
            edu_levels[edu_level.code] = edu_level.id 
        return edu_levels
    
    def _read_csv(self, file, options):
        """ Returns a CSV-parsed iterator of all empty lines in the file

        :throws csv.Error: if an error is detected during CSV parsing
        :throws UnicodeDecodeError: if ``options.encoding`` is incorrect
        """
        csv_iterator = csv.reader(
            StringIO(file),
            quotechar=str(options['quoting']),
            delimiter=str(options['separator']))

        def nonempty(row):
            return any(x for x in row if x.strip())

        csv_nonempty = itertools.ifilter(nonempty, csv_iterator)
        # TODO: guess encoding with chardet? Or https://github.com/aadsm/jschardet
        encoding = options.get('encoding', 'utf-8')
        return itertools.imap(
            lambda row: [item.decode(encoding) for item in row],
            csv_nonempty)
    
    def get_respondent_vals(self, row):
        vals = {'is_respondent':True, 'informed_by_mail':True,'informed_by_sms':True}
        
        countries = self.get_country_dict()
        
        for file_field in HEADER_NORMAL:
            model_field = MAPPER[file_field]
            if model_field and row[HEADER.index(file_field)] != 'NULL':
                try:
                    vals[model_field] = str(row[HEADER.index(file_field)].encode('utf-8'))
                except Exception, e:
                    vals[model_field] = str(row[HEADER.index(file_field)].encode('iso-8859-1'))
        
        for file_field in HEADER_BOOLEAN:
            model_field = MAPPER[file_field]
            if model_field:
                if row[HEADER.index(file_field)] == 'NULL' or row[HEADER.index(file_field)] == '0':
                    vals[model_field] = False
                else:
                    vals[model_field] = True
        
        for file_field in HEADER_MARITAL_STATUS:
            if row[HEADER.index(file_field)] == '1':
                vals['marital_status'] = MAPPER[file_field]
                break
        for file_field in HEADER_PROFESSION:
            if row[HEADER.index(file_field)] == '1':
                if file_field == "pinfo_profession_independent_comp":
                    vals['profession_indie_comp'] = True
                else:
                    vals['professional_status'] = MAPPER[file_field]
                break
        
        if row[HEADER.index('pinfo_nationality_country_id')] != 'NULL':
            vals['nationality_id'] = countries[COUNTRY_FILE[str(row[HEADER.index('pinfo_nationality_country_id')].encode('utf-8'))]]
        if row[HEADER.index('pinfo_country_id')] != 'NULL':
            vals['country_id'] = countries[COUNTRY_FILE[str(row[HEADER.index('pinfo_country_id')].encode('utf-8'))]]
    
        return vals
    
    def get_customer_vals(self,row,countries):
        vals = {'is_company':True}
        for file_field in CUSTOMER_HEADER:
            model_field = CUSTOMER_MAPPER[file_field]
            if model_field and model_field == 'lastname' and row[CUSTOMER_HEADER.index(file_field)] == '':
                vals['lastname'] = "NONAME"
            elif model_field and row[CUSTOMER_HEADER.index(file_field)] != 'NULL' and row[CUSTOMER_HEADER.index(file_field)] != '':
                if model_field == 'country_id':
                   vals['country_id'] = countries[(row[CUSTOMER_HEADER.index('country_code')].encode('utf-8'))]
                else:    
                    try:
                        vals[model_field] = str(row[CUSTOMER_HEADER.index(file_field)].encode('utf-8'))
                    except Exception, e:
                        vals[model_field] = str(row[CUSTOMER_HEADER.index(file_field)].encode('iso-8859-1'))
        
        return vals
    
    def get_group_vals(self,row,customers):
        vals = {}
        for file_field in GROUP_HEADER:
            model_field = GROUP_MAPPER[file_field]
            
            if model_field and row[GROUP_HEADER.index(file_field)] != 'NULL' and row[GROUP_HEADER.index(file_field)] != '':
                if model_field == 'customer':
                   vals['customer'] = customers[(row[GROUP_HEADER.index('ref_client')])]
                elif model_field == 'start_date':
                    vals['start_date'] = str(row[GROUP_HEADER.index('date_etude')])
                    vals['end_date'] = str(row[GROUP_HEADER.index('date_etude')])
                else:    
                    try:
                        vals[model_field] = str(row[GROUP_HEADER.index(file_field)].encode('utf-8'))
                    except Exception, e:
                        vals[model_field] = str(row[GROUP_HEADER.index(file_field)].encode('iso-8859-1'))
        
        return vals
    
    def get_note_vals(self,row,respondents):
        vals = {}
        for file_field in NOTE_HEADER:
            if respondents.get(row[NOTE_HEADER.index('reference')],False):
                model_field = NOTE_MAPPER[file_field]
                if model_field == 'name' and row[NOTE_HEADER.index('note')] == '':
                    vals['name'] = 'No Message'
                elif model_field and row[NOTE_HEADER.index(file_field)] != 'NULL' and row[NOTE_HEADER.index(file_field)] != '':
                    if model_field == 'partner_id':
                       vals['partner_id'] = respondents[(row[NOTE_HEADER.index('reference')])]
                    else:    
                        try:
                            vals[model_field] = str(row[NOTE_HEADER.index(file_field)].encode('utf-8'))
                        except Exception, e:
                            vals[model_field] = str(row[NOTE_HEADER.index(file_field)].encode('iso-8859-1'))
            else:
                return False
        return vals
                
    def create_respondent(self,vals, template_user_id):
         # ref_number must replace by email to go on production
        #res_user_id = self.pool.get('res.users').copy(self.env.cr, self.env.uid, template_user_id, {'login':vals['ref_number']}, self.env.context)
        res_user_id = self.pool.get('res.users').copy(self.env.cr, self.env.uid, template_user_id, {'login':vals['email']}, self.env.context)
        res_user = self.env['res.users'].browse(res_user_id)
        
        # remove this line to go on production
        #vals['email'] = 'test@opinions.be'
        res_user.partner_id.write(vals)
        
        return True 
    
    def import_respondent(self, rows):
        ir_config_parameter = self.env['ir.config_parameter']
        template_user_id = literal_eval(ir_config_parameter.get_param('defiline.template_respondent_id', 'False'))
        for row in rows:
            vals = self.get_respondent_vals(row)

            self.create_respondent(vals, template_user_id)
        
        return True
    
    def import_customer(self, rows):
        countries = self.get_country_dict()
        for row in rows:
            vals = self.get_customer_vals(row,countries)
            self.env['res.partner'].create(vals)
        
        return True
    
    def import_group(self, rows):
        customers = self.get_customer_dict()
        for row in rows:
            vals = self.get_group_vals(row, customers)
            self.env['event.event'].create(vals)
        
        return True

    def import_note(self, rows):
        respondents = self.get_respondent_dict()
        for row in rows:
            vals = self.get_note_vals(row, respondents)
            if vals:
                self.env['crm.phonecall'].create(vals)
        
        return True   
    
    def import_participation(self, rows):
        respondents = self.get_respondent_dict()
        groups = self.get_group_dict()
        
        for row in rows:
            respondent_id = respondents.get(row[1],False)
            event_id = groups[row[0]]
            if respondent_id:
                subscription = self.env['event.registration'].create({'partner_id':respondent_id, 'event_id':event_id})
                subscription._onchange_partner()
        
        return True  
    
    @api.one
    def import_csv(self):
        options = {'encoding':'utf-8','separator':',','quoting':'"'}
        rows = self._read_csv(base64.b64decode(self.file), options)
        rows = list(itertools.islice(rows,1, None))
        
        if self.type == "count":
            print "csv file contains : " + str(len(rows)) +" rows"
        elif self.type =="missing":
            missing_index = []
            vals_list = []
            db_ref = self.env['res.partner'].search([('is_respondent','=',True)]).mapped('ref_number')
            for row in rows:
                if row[0] not in db_ref:
                    missing_index.append(rows.index(row))
                    vals_list.append(self.get_respondent_vals(row))
            
            ir_config_parameter = self.env['ir.config_parameter']
            template_user_id = literal_eval(ir_config_parameter.get_param('defiline.template_respondent_id', 'False'))
                
            for vals in vals_list:
                self.create_respondent(vals,template_user_id)
        elif self.type == "bad_sab":
            resp_sab_bad = {}
            respondents = self.env['res.partner'].search([('is_respondent','=',True)])
            
            for row in rows:
                for i in range (1,8) :
                    print
                resp_sab_bad[row[0]] = row[1].lower()
            
            for respondent in respondents:
                if resp_sab_bad.get(respondent.ref_number,False):
                    respondent.status = resp_sab_bad.get(respondent.ref_number)
        elif self.type == "lang_and_so":
            #langs = self.get_language_dict()
            titles = self.get_title_dict()
            edu_levels = self.get_edu_level_dict()
            resp_missing_fields = {}
            missing_fields_values = {}
            respondents = self.env['res.partner'].search([('is_respondent','=',True)])
            
            for row in rows:
                vals = {}
                for header in HEADER_SPECIAL_PARSE:
                    if row[HEADER_SPECIAL_PARSE.index(header)] != 'NULL' and row[HEADER_SPECIAL_PARSE.index(header)] != '0' and row[HEADER_SPECIAL_PARSE.index(header)] != '':
                        if header == 'participant_language_id':
                            vals['lang'] = LANGUAGE_FILE[str(row[HEADER_SPECIAL_PARSE.index('participant_language_id')])]
                        elif header == 'pinfo_title_id':
                            vals['title'] = titles[TITLE_FILE[str(row[HEADER_SPECIAL_PARSE.index('pinfo_title_id')])]]
                        elif header == 'pinfo_availability':
                            vals['availability'] = AVAILABILITY_FILE[row[HEADER_SPECIAL_PARSE.index('pinfo_availability')]]
                        elif header == 'pinfo_education_level_id':
                            vals['edu_level_id'] = edu_levels[EDU_LEVEL_FILE[row[HEADER_SPECIAL_PARSE.index('pinfo_education_level_id')]]]
                        elif header == 'pinfo_partner_education_level_id':
                            vals['partner_edu_level_id'] = edu_levels[EDU_LEVEL_FILE[row[HEADER_SPECIAL_PARSE.index('pinfo_partner_education_level_id')]]]
                if len(vals) > 0:
                    missing_fields_values[row[0]] = vals
            
            for respondent in respondents:
                if missing_fields_values.get(str(respondent.ref_number),False):
                    respondent.write(missing_fields_values.get(str(respondent.ref_number)))
        elif self.type == "update_group_customer":
            group_cust = {}
            customer_list = self.get_customer_dict()
            
            groups = self.env['event.event'].search([])
            
            for row in rows:
                if customer_list.get(row[2],False):
                    group_cust[row[0]] = customer_list[row[2]]
            
            for group in groups:
                if group_cust.get(group.reference_number,False):
                    group.customer_id = group_cust[group.reference_number]
                    group._onchange_customer_id()
            
        elif self.type == "respondent":
            self.import_respondent(rows)
        elif self.type == "customer":
            self.import_customer(rows)
        elif self.type == "group":
            self.import_group(rows)
        elif self.type == "notes":
            self.import_note(rows)
        elif self.type == "participation":
            self.import_participation(rows)
        return {'type': 'ir.actions.act_window_close'}
        
    
