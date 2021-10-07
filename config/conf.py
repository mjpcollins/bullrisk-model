import os


settings = {'port': int(os.environ.get("PORT", 8080)),
            'project': 'national-rail-247416',
            'egress-bucket': 'bullrisk-egress',
            'dataset': 'bullrisk',
            'bigquery-writer': 'https://bills-bigquery-slam-nmgxkhvw5a-nw.a.run.app/upload'}
