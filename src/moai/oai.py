from datetime import datetime

import oaipmh
import oaipmh.metadata
import oaipmh.server
import oaipmh.error

from moai.metadata import get_writer

class OAIServer(object):
    def __init__(self, db, config):
        self.db = db
        self.config = config

    def identify(self):
        return oaipmh.common.Identify(
            repositoryName=self.config.name,
            baseURL=self.config.url,
            protocolVersion='2.0',
            adminEmails=self.config.admins,
            earliestDatestamp=datetime(2001, 1, 1, 10, 00),
            deletedRecord='transient',
            granularity='YYYY-MM-DDThh:mm:ssZ',
            compression=['identity'])
    
    def listSets(self, cursor=0, batch_size=20):
        for set in self.db.oai_sets(cursor, batch_size):
            oai_id = self.config.get_setspec_id(set['id'])
            yield [oai_id, set['name'], set['description']]

    def listRecords(self, metadataPrefix, set=None, from_=None, until=None,
                    cursor=0, batch_size=10):
        
        self._checkMetadataPrefix(metadataPrefix)
        for record in self._listQuery(set, from_, until, cursor, batch_size):
            header, metadata = self._createHeaderAndMetadata(record)
            yield header, metadata, None

    def listIdentifiers(self, metadataPrefix, set=None, from_=None, until=None,
                        cursor=0, batch_size=10):
        
        self._checkMetadataPrefix(metadataPrefix)
        for record in self._listQuery(set, from_, until, cursor, batch_size):
            yield self._createHeader(record)

    def _checkMetadataPrefix(self, metadataPrefix):
        if metadataPrefix not in self.config.metadata_prefixes:
            raise oaipmh.error.CannotDisseminateFormatError

    def _createHeader(self, record):
        oai_id = self.config.get_oai_id(record['record']['id'])
        datestamp = record['record']['when_modified']
        sets = [self.config.get_setspec_id(s) for s in record['sets']]
        deleted = record['record']['deleted']
        return oaipmh.common.Header(oai_id, datestamp, sets, deleted)

    def _createHeaderAndMetadata(self, record):
        header = self._createHeader(record)
        metadata = oaipmh.common.Metadata(record['metadata'])
        metadata.record = record
        return header, metadata
    
    def _listQuery(self, set, from_, until, 
                   cursor, batch_size, identifier=None):

        if identifier:
            identifier = self.config.get_internal_id(identifier)
        if set:
            set = self._get_internal_set_id(set)
            
        now = datetime.now()
        if until != None and until > now:
            # until should never be in the future
            until = now
            
        if self.config.delay:
            # subtract delay from until_ param, if present
            if until is None:
                until = datetime.now()
            until = until.timetuple()
            ut = time.mktime(until)-self.filter_data.delay
            until = datetime.fromtimestamp(ut)
            
        if set is None:
            sets = []
        else:
            sets = [set]

        sets += self.config.sets_allowed
        filtersets = self.config.filter_sets
        notsets = self.config.sets_disallowed    
        
        return self.db.oai_query(offset=cursor,
                                 batch_size=batch_size,
                                 sets=sets,
                                 not_sets=notsets,
                                 filter_sets=filtersets,
                                 from_date=from_,
                                 until_date=until,
                                 identifier=identifier
                                 )

def OAIServerFactory(db, config):
    metadata_registry = oaipmh.metadata.MetadataRegistry()
    for prefix in config.metadata_prefixes:
        metadata_registry.registerWriter(prefix,
                                         get_writer(prefix, config, db))
            
    return oaipmh.server.BatchingServer(
        OAIServer(db, config),
        metadata_registry=metadata_registry,
        resumption_batch_size=config.batch_size
        )