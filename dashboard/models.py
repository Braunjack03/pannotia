from flask_login import UserMixin
import boto3
from boto3.dynamodb.conditions import Key
import json
from decimal import Decimal
from datetime import datetime as dt

dynamodb_resource = boto3.resource('dynamodb', region_name='ap-southeast-2')
dynamodb_client = boto3.client('dynamodb', region_name='ap-southeast-2')


class User(UserMixin):
    def __init__(self, email, name, level, password):
        self.email = email
        self.name = name
        self.level = level
        self.password = password

    def add(self, table):
        table = dynamodb_resource.Table(table)
        table.put_item(
            Item={
                'name': self.name,
                'email': self.email,
                'password': self.password,
                'level': self.level,
            }
        )

    def get_id(self):
        return self.email

    @staticmethod
    def query(email, table):
        table = dynamodb_resource.Table(table)
        response = table.get_item(
            Key={"email": email}
        )
        user = None
        if response.get('Item'):
            item = response['Item']
            name = item['name']
            password = item['password']
            level = item['level']
            user = User(email, name, level, password)
        return user


class Dynamo:
    table_name = None
    pk_name = ''

    def __init__(self, table_name, key_name):
        self.table_name = table_name
        self.pk_name = key_name

    @staticmethod
    def format_lead(lead):
        lead['updates'] = json.loads(lead['updates'])
        lead['status'] = {}
        lead['checkout'] = json.loads(lead.get('checkout', "[]"))
        for l in lead['updates']:
            for key in l:
                if not l.get(key, None) is None:
                    lead['status'][key] = l[key]
        return lead

    def read_table_item(self, pk_value, key_name=None, index_name=None):
        table = dynamodb_resource.Table(self.table_name)
        if key_name and index_name:
            temp = table.query(IndexName=index_name, KeyConditionExpression=Key(key_name).eq(pk_value))
            response = temp
            while temp.get('LastEvaluatedKey'):
                temp = table.query(IndexName=index_name, KeyConditionExpression=Key(key_name).eq(pk_value),
                                   ExclusiveStartKey=temp['LastEvaluatedKey'])
                response['Items'] += temp['Items']
        else:
            response = table.get_item(Key={self.pk_name: pk_value})
        return response

    def update_table_item(self, pk_value, col_dict):
        table = dynamodb_resource.Table(self.table_name)
        now = int(dt.now().timestamp())
        update = Decimal(now)
        attr = {"#update": "update", "#state": "state"}
        val = {":update": update, ":state": Decimal(col_dict.get('state', 0))}
        set_str = 'SET #update = :update, #state = :state,'
        key = 'updates'
        updates = col_dict[key][-1]
        progress = int(col_dict.get('progress', 0))
        state = int(col_dict.get('state', 0))
        invoice = int(col_dict.get('invoice', 0))
        if invoice > 0:
            attr["#invoice"] = "invoice"
            val[":invoice"] = Decimal(invoice)
            set_str += ' #invoice = :invoice,'
        if 'update' not in updates.keys():
            updates['update'] = now
            updates['progress'] = int(progress)
            updates['state'] = int(state)
        if updates.get('state', 0) != state or updates.get('progress', 0) != progress or updates.get('invoice',
                                                                                                     0) != invoice:
            col_dict[key].append({'update': now,
                                  'progress': int(progress),
                                  'state': int(state),
                                  })
        for key in col_dict.keys():
            if key in [self.pk_name, 'update', 'state', 'invoice']:
                continue
            if key in ['checkout', 'updates']:
                if type(col_dict[key]) == dict or type(col_dict[key]) == list:
                    col_dict[key] = json.dumps(col_dict[key])
            if col_dict[key] == '':
                col_dict[key] = None
            attr[f'#{key.replace(" ", "")}'] = f'{key}'
            val[f':{key.replace(" ", "")}'] = f'{col_dict[key]}'
            set_str += f' #{key.replace(" ", "")} = :{key.replace(" ", "")},'
        set_str = set_str[:-1]
        response = table.update_item(
            Key={self.pk_name: pk_value},
            UpdateExpression=set_str,
            ExpressionAttributeNames=attr,
            ExpressionAttributeValues=val
        )
        return response

    def add(self, key_value, dict_items):
        self.update_table_item(key_value, dict_items)
        return

    def get(self, key_value, key_name=None, index_name=None):
        response = self.read_table_item(key_value, key_name, index_name)
        if 'Item' in response:
            return self.format_lead(response['Item'])
        elif 'Items' in response:
            leads = []
            for lead in response['Items']:
                leads.append(self.format_lead(lead))
            return leads
        return None

    def update_state(self, lead_id, state):
        lead = self.get(lead_id)
        lead['state'] = Decimal(state)
        self.update_table_item(lead_id, lead)

    def update_seen(self, lead_id):
        lead = self.get(lead_id)
        state = lead.get('state', 9999)
        if state // 100 == 1:
            lead['state'] = Decimal(110)
        elif state // 100 == 2:
            lead['state'] = Decimal(210)
        elif state // 100 == 3:
            lead['state'] = Decimal(310)
        elif state // 100 == 4:
            lead['state'] = Decimal(410)
        else:
            return
        self.update_table_item(lead_id, lead)

    def delete(self, key_value):
        table = dynamodb_resource.Table(self.table_name)
        table.delete_item(
            Key={
                self.pk_name: key_value,
            }
        )
