"""Utilities for adding domains to a geodatabase
"""
import os
import arcpy


def add_domain(in_workspace, domain_name, domain_description=None,
               field_type="SHORT", domain_type="CODED", values=None,
               replace_existing_domain=False):
    """Adds a domain to a specified workspace.

    For description of parameters, see documentation for:
    * arcpy.management.CreateDomain
    * arcpy.management.AddCodedValueToDomain

    Parameters
    ----------
    in_workspace : str
    domain_name : str
    domain_description : str
    field_type : str
    domain_type : str
    values : list or dict
        Values to be added to the domain.
    replace_existing_domain : bool
        Determines what happens if you try to add a domain with a name that
        matches an already existing domain.
        * True: Deletes the preexisting domain
        * False: Leaves the existing domain alone and does nothing else to it.
    """
    # Get list of existing domains
    existing_domains = arcpy.da.ListDomains(in_workspace)

    # Check to see if the specified domain already exists
    domain_exists = False
    for domain in existing_domains:
        if domain.name == domain_name:
            domain_exists = True
            break

    if domain_exists:
        if replace_existing_domain:
            arcpy.management.DeleteDomain(in_workspace, domain_name)
        else:
            arcpy.AddMessage('Domain "%s" already exists in "%s".' % (
                domain_name, os.path.basename(in_workspace)))
            return

    # Create domain and add values
    arcpy.management.CreateDomain(in_workspace, domain_name,
                                  domain_description, field_type, domain_type)
    if values is not None:
        if isinstance(values, list):
            code = 0
            for code_description in values:
                arcpy.management.AddCodedValueToDomain(in_workspace,
                                                       domain_name,
                                                       code,
                                                       code_description)
                code = code + 1
        elif isinstance(values, dict):
            for code_description, code in values.iteritems():
                arcpy.management.AddCodedValueToDomain(in_workspace,
                                                       domain_name,
                                                       code,
                                                       code_description)
