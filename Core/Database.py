# -*- coding: UTF-8 -*-
'''
Created on May 14, 2014

@author: Furqan Wasi

'''

from Core import SharedApp
import sqlite3

class Database(object):
    _instance = None
    def __init__(self):
        Database._instance = object.__new__(Database)
        Database._instance.Fixity = SharedApp.SharedApp.App
        Database._instance._tableConfiguration = 'configuration'
        Database._instance._tableProject = 'project'
        Database._instance._tableProjectPath = 'projectPath'
        Database._instance._tableVersionDetail = 'versionDetail'
        Database._instance._tableVersions ='versions'
        Database._instance.connect()
        Database._instance.con = None
        Database._instance.cursor = None
        Database._instance.timeSpan = 1


    @staticmethod
    def getInstance():
        if not isinstance(Database._instance, Database):
            Database._instance = object.__new__(Database)
            Database._instance.Fixity = SharedApp.SharedApp.App
            Database._instance._tableConfiguration = 'configuration'
            Database._instance._tableProject = 'project'
            Database._instance._tableProjectPath = 'projectPath'
            Database._instance._tableVersionDetail = 'versionDetail'
            Database._instance._tableVersions ='versions'
            Database._instance.connect()
            Database._instance.con = None
            Database._instance.cursor = None
            Database._instance.timeSpan = 1

        return Database._instance

    def selfDestruct(self):
        del self

    def connect(self):
        try:
            self.con = sqlite3.connect(self.Fixity.Configuration.getDatabaseFilePath())
            self.cursor = self.con.cursor()
        except:
            self.Fixity.logger.LogException(Exception.message)
            pass

    #Get one record using given sql query
    #@param query: SQL Raw Query
    #
    #@return: One sQuery Result

    def getOne(self, query):
        try:
            self.cursor.execute(query)
            self.con.commit()
            Row = self.cursor.fetchone()
            return Row
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False



    #SQL Query Runner
    #@param query: SQL Raw Query
    #
    #@return: Query Result

    def sqlQuery(self, query):
        try:
            response = self.cursor.execute(query)
            self.con.commit()
            return response
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False

    #Get Project Information
    #@param projectName: Project Name to be searched in database
    #@param limit: If Ture 1 limit with be applied
    #
    #@return project information

    def getProjectInfo(self,projectName = None, limit = True):
        response = {}
        try:
            information = {}
            information['id'] = None
            limit = ' '
            condition = None
            if limit:
                limit  = " LIMIT 1"

            if projectName:
                condition ="title like '"+projectName+"' " + limit

            return self.select(self._tableProject, '*', condition)

        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False

    #Get Projects paths Information
    #@param project_id: Project ID
    #@param version_id: ID of Version of Project to be fetched
    #
    #@return project information

    def getProjectPathInfo(self ,project_id ,version_id):
        try:
            self.connect()
            information = {}
            information['id'] = None
            response = self.select(self._tableProjectPath, '*', "projectID='"+str(project_id)+"' and versionID = '"+ str(version_id) + "'")
            
            return response
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False





    #Get SMTP and User Email Configuration
    #@return Configuration


    def getConfiguration(self):
        try:
            response = self.select(self._tableConfiguration, '*')
            return response
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False




    #Get Given Version Details
    #@param project_id: Project ID
    #@param version_id: ID of Version of Project who's detail to be fetched
    #@param order_by: Order By
    #
    #@return project information

    def getVersionDetails(self, project_id, version_id, pathID, where, OrderBy=None):
        try:
            response = self.select(self._tableVersionDetail, '*'," projectID='"+str(project_id)+"' and versionID='"+str(version_id)+"' and "+where,  OrderBy)
            return response
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False

    ''' Fetch information related to email configuration'''
    def getConfigInfo(self, project=None):
        queryResult = self.select(self._tableConfiguration)
        try:
            if len(queryResult)>0 :
                information = {}
                for  result in queryResult:
                    information['id'] = queryResult[result]['id']
                    information['smtp'] = self.DecodeInfo(queryResult[result]['smtp'])
                    information['email'] = self.DecodeInfo(queryResult[result]['email'])
                    information['pass'] = self.DecodeInfo(queryResult[result]['pass'])
                    information['port'] = queryResult[result]['port']
                    information['protocol'] = queryResult[result]['protocol']
                    information['debugger'] = queryResult[result]['debugger']
                    break;
                return information
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False
        return {}






    #Get Last Inserted Version of given project
    def getVersionDetailsLast(self, project_id, path_id, where):

        try:
            response = {}
            result_of_last_version = self.select(self._tableVersionDetail, '*', "projectID='" + str(project_id) +"' and "+ where, ' versionID DESC LIMIT 1')
            if(len(result_of_last_version) > 0):
                response = self.getVersionDetails(project_id, result_of_last_version[0]['versionID'], path_id,  where, ' id DESC')
            return response
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False





    #Convert List to Tuple Data type
    def listToTuple(self, proveded_list):
        try:
            new_list = []
            for single_of_proveded_list in  proveded_list:
                new_list.append(proveded_list[single_of_proveded_list])
            return tuple(new_list)

        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False

    def commit(self):
        self.con.commit()





    #SQL Select Query
    #@param table_name: Table Name
    #@param select: Column To Select
    #@param condition: Conditions as String
    #@param order_by: order By Columns
    #
    #@return: Query Result

    def select(self,tableName,  select  = '*', condition=None,orderBy = None):
        try:

            query = 'SELECT '+ str(select) +' FROM '+str(table_name)
            if(condition is not None):
                query += ' WHERE ' + condition
            if(order_by is not None):
                query += ' ORDER BY '+ order_by
            print(query)
            response = {}
            response_counter = 0
            for r in self.dict_gen(self.cursor.execute(query)):
                response[response_counter] = r
                response_counter = response_counter + 1
            self.commit()


            return response
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False







    #Query Result to list converter

    def dict_gen(self,curs):
        try:
            import itertools
            field_names = [d[0] for d in curs.description]
            while True:
                rows = curs.fetchmany()
                if not rows: return
                for row in rows:
                    yield dict(itertools.izip(field_names, row))

        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            pass






    #SQL Insert Query
    #@param table_name: Table Name
    #@param information: List of columns with Values (index as Column and Value as Column Value)
    #
    #@return: Insert Id of this record


    def insert(self, table_name, information):
        try:
            query = 'INSERT INTO '+str(table_name)
            values = {}
            columnName = {}
            counter = 0
            for index in information:
                try:
                    columnName[str(counter)] = index
                    values[str(counter)]  = str(information[index])

                    counter = counter + 1
                except:
                    pass

            query = query + ' ( '+self.implode ( columnName,  ',  ') + ' ) VALUES ( ' + self.implode(values,  ' , ', False) + ' ) '



            self.cursor.execute(query)
            self.commit()
            return {'id':self.cursor.lastrowid}
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False


    #SQL Delete Query
    #@param table_name: Table Name
    #@param condition: Condition of which row will deleted
    #
    #@return: Response of Query Result

    def delete(self,table_name ,condition):
        try:
            query = 'DELETE FROM '+str(table_name) + ' WHERE '+ condition
            response = self.sqlQuery(query)
            
            return response
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False

      #SQL Update Query
      #@param table_name: Table Name
      #@param information: List of columns with Values (index as Column and Value as Column Value)
      #@param condition: Condition of which row will deleted
      #
      #@return: Response of Query Result

    def update(self, table_name, information, condition):
        try:
            query = 'UPDATE '+str(table_name) +' SET '
            counter = 0
            for single_info in information:

                    if counter == 0:
                        query += str(single_info) + "='" + str(information[single_info]) + "'"
                    else:
                        query += ' , '+ str(single_info) + "='" + str(information[single_info]) + "'"
                    counter = counter+1
            query += ' WHERE '+condition

            response = self.cursor.execute(query)
            self.commit()
            return response

        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False


    #  Columns and records Implode for query
    #  @param information: Array of Value to be imploded
    #  @param glue: glue with values will be glued
    #  @param isColumn: Given Information is of tables columns or Row
    #
    #  @return: Response of Query Result


    def implode(self,information , glue , isColumn = True):
        try:
            counter = 0
            string_glued = ''
            for info in information:
                try:
                    if isColumn:
                        if(counter == 0):
                            string_glued = string_glued + information[info]
                        else:
                            string_glued =  string_glued + ' , ' + information[info]

                    else:
                        if(counter == 0):
                            string_glued = string_glued + ' "'+ str(information[info])+ '" '
                        else:
                            string_glued =  string_glued + ' , "' + information[info]+ '" '
                    counter = counter + 1
                except Exception as e:
                    pass

            return string_glued
        except (sqlite3.OperationalError,Exception):
            self.Fixity.logger.LogException(Exception.message)
            return False