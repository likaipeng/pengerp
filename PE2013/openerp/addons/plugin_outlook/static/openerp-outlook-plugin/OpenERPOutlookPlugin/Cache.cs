/*
    PengERP, Open Source Business Applications
    Copyright (c) 2011 LKP <http://pengerp.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


using System.Collections;
using PengERPClient;

namespace PengERPOutlookPlugin
{
    static public  class Cache
    {
        static private PengERPOutlookPlugin _openerp;
        static public PengERPOutlookPlugin PengERPOutlookPlugin
        {
            get
            {
                return _openerp;
            }
            set
            {

                _openerp = value;
            }
        }
        static private Model[] document_models;
        static public Model[] DocumentModelList
        {
            get
            {
                return document_models;
            }
            set
            {

                document_models = value;
            }
        }        

    }
}
