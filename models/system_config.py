from database import db
from datetime import datetime

class SystemConfig(db.Model):
    __tablename__ = 'system_config'
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(SystemConfig, self).__init__(**kwargs)

    @classmethod
    def get_settings(cls):
        configs = cls.query.all()
        return {c.key: c.value for c in configs}

    @classmethod
    def set_settings(cls, settings_dict):
        for k, v in settings_dict.items():
            config = cls.query.filter_by(key=k).first()
            if config:
                config.value = str(v)
            else:
                config = cls(key=k, value=str(v))
                db.session.add(config)
        db.session.commit()
