#!/usr/bin/env python
# coding: utf-8

# In[47]:


from ixnetwork_restpy import SessionAssistant
from typing import List



session_assistant = SessionAssistant(IpAddress="10.36.236.121", UserName="admin", Password="Kimchi123Kimchi123!",
                            LogLevel=SessionAssistant.LOGLEVEL_INFO, 
                            ClearConfig=False,
                            SessionId=5)


# In[48]:


ixnetwork = session_assistant.Ixnetwork


# In[49]:


def getStatView(caption):
    """
    Get a statistics view.
    :param caption: <str>: The statistics view caption name.
                       Example: Protocols Summary, Flow Statistics, etc.
    Return
       The statistics view object attributes.
    """
    viewResults = []
    counterStop = 60
    for counter in range(1, counterStop+1): 
        print('\nWaiting for statview: {0}\n'.format(caption))
        viewResults = ixnetwork.Statistics.View.find(Caption=caption)
        if counter < counterStop and len(viewResults) == 0:
            print('\n{0} is not ready yet. Wait {1}/{2} seconds\n'.format(caption, counter, counterStop))
            time.sleep(1)
            continue

        if counter < counterStop and len(viewResults) != 0:
            print('\n{0} is ready\n'.format(caption))
            return viewResults

        if counter == counterStop and len(viewResults) == 0 :
            raise Exception('\nAPI server failed to provide stat views')
            
def getStatViewResults(statViewName=False, getColumnCaptions=False, getPageValues=False, rowValuesLabel=None, getTotalPages=False, timeout=60):
        """
        Wait for a statistic view to be ready with stats. Cannot assume the stats are ready.
        For example, if startAllProtocols was executed, protocol summary stats may not be ready
        provided by the API server.
    
        This function takes in statViewName as a mandatory parameter.
        
        Note:
           Getting stats is always a two step process.  You normally need to get the statview and then
           get the stat page values.  You must verify each seperately for readiness.
        :param statViewName: <Mandatory>: The name of the stat view sucha as:
                         Protocols Summary, Port Statistics, Flow Statistics, Traffic Item Statistics, etc.
        :param getColumnCaptions: <bool>: Optional: Returns the statViewName column caption names in a list.
        :param getPageValues: <bool>: Optional: Returns the statViewName page values in a list.
        :param rowValuesLabel: <str>: Optional: Return the stats for just the row's label name. 
        :param getTotalPages: <bool>: Optional: Return the total amount of pages for the statview.
        Example 1:
           # Wait for statViewName='Protocols Summary' to be ready and return the data.
           results = self.getStatView(caption='Protocols Summary')
   
        Example 2:
           # Wait for each statViewName to be ready.
           # Then get the column captions, which are the names of the stats 
           # and get the page values, which are the stat values for each caption.
           columnCaptions = self.getStatViewResults(statViewName='Protocols Summary', getColumnCaptions=True)
           pageValues = self.getStatViewResults(statViewName='Protocols Summary', getPageValues=True)
        Example 3:
            columnCaptions= statObj.getStatViewResults(statViewName='Traffic Item Statistics', getColumnCaptions=True)
            trafficItemStats = statObj.getStatViewResults(statViewName='Traffic Item Statistics',
                                                          rowValuesLabel=trafficItemName)
            txFramesIndex = columnCaptions.index('Tx Frames')
            rxFramesIndex = columnCaptions.index('Rx Frames')
        """
        # Verify for statViewName readiness first
        getStatView(caption=statViewName)

        viewResults = []
        counterStop = timeout
        for counter in range(1, counterStop+1): 
            if getColumnCaptions:
                print('\nWaiting for {0} Data.ColumnCaptions\n'.format(statViewName))
                viewResults = ixnetwork.Statistics.View.find(Caption=statViewName)[0].Data.ColumnCaptions
                deeperView = 'Data.ColumnCaptions'

            if getPageValues:
                print('\nWaiting for {0} Data.PageValues\n'.format(statViewName))
                viewResults = ixnetwork.Statistics.View.find(Caption=statViewName)[0].Data.PageValues
                deeperView = 'Data.PageValues'

            if getTotalPages:
                print('\nWaiting for {0} Data.TotalPages\n'.format(statViewName))
                return ixnetwork.Statistics.View.find(Caption=statViewName)[0].Data.TotalPages

            if rowValuesLabel is not None:
                print('\nWaiting for {0} Data.GetRowValues\n'.format(statViewName))
                viewResults = ixnetwork.Statistics.View.find(Caption=statViewName)[0].GetRowValues(Arg2=rowValuesLabel)
                deeperView = 'GetRowValues'

            if counter < counterStop and len(viewResults) == 0:
                print('\n{0} {1}: is not ready yet.\n\tWait {2}/{3} seconds\n'.format(statViewName, deeperView,
                                                                                        counter, counterStop))
                time.sleep(1)
                continue

            if counter < counterStop and len(viewResults) != 0:
                print('\n{0} {1}: is ready\n'.format(statViewName, deeperView))
                return viewResults

            if counter == counterStop and len(viewResults) == 0 :
                raise Exception('\nAPI server failed to provide stat views for {0} {1}'.format(statViewName, deeperView))


                
def getStatsByRowLabelName(statViewName=None, rowLabelName='all', timeout=90):
        """
        This is an internal helper function for: getTrafficItemStats, getPortStatistics, getProtocolsSummary,
                                                 getGlobalProtocolStatistics, getDataPlanePortStatistics.
        These stats are identified by a label name for each row shown in the GUI.
        The label name is the first column value shown in the GUI.
        :param statViewName: 'Port Statistics', 'Traffic Item Statistics', 'Protocols Summary', 'Port CPU Statistics'
                             'Global Protocol Statistics', 'Data Plane Statistics'
        :param rowLabelName: <str|list|all>: If you look at the IxNetwork GUI for any of the statViewName listed above, 
                                             their rowLabelName is the first in the column stats.
                             If you're just getting one specific stat, pass in the rowLabelName.
                             If you want to get multiple stats, pass in a list of rowLabelName.
                             Defaults to return all the row of stats.
        Return
           A dict: stats
        """
        columnNames = getStatViewResults(statViewName=statViewName, getColumnCaptions=True)
        totalPages = getStatViewResults(statViewName=statViewName, getTotalPages=True)
        stats = {}

        if type(rowLabelName) == list or rowLabelName == 'all':
            for pageNumber in range(1, totalPages+1):
                ixnetwork.Statistics.View.find(Caption=statViewName)[0].Data.CurrentPage = pageNumber

                statViewValues = getStatViewResults(statViewName=statViewName, getPageValues=True)

                if type(rowLabelName) == list:
                    # Get the specified list of traffic item's stats
                    for eachViewStats in statViewValues:
                        currentRowLabelName = eachViewStats[0][0]
                        if currentRowLabelName in rowLabelName:
                            stats[currentRowLabelName] = {}
                            for columnName, statValue in zip(columnNames, eachViewStats[0]):
                                stats[currentRowLabelName][columnName] = statValue

                else:
                    # Get all the traffic items
                    for eachViewStat in statViewValues:
                        currentRowLabelName = eachViewStat[0][0]
                        stats[currentRowLabelName] = {}                
                        for columnName, statValue in zip(columnNames, eachViewStat[0]):
                            stats[currentRowLabelName][columnName] = statValue
        else:
            # Get just one traffic item stat
            statViewValues = getStatViewResults(statViewName=statViewName, rowValuesLabel=rowLabelName, timeout=timeout)
            if statViewValues == 'kVoid':
                raise Exception('No such port name found.  Verify for typo: {}'.format(rowLabelName))

            stats[rowLabelName] = {}
            for columnName, statValue in zip(columnNames, statViewValues):
                stats[rowLabelName][columnName] = statValue

        return stats

    
a = getStatsByRowLabelName(statViewName='Port CPU Statistics', rowLabelName="all", timeout=60)
print(a)

b = getStatsByRowLabelName(statViewName='Port Statistics', rowLabelName="all", timeout=60)
print(b)


# In[ ]:




