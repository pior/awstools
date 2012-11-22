import unittest

import mock

from awstools import application

# class TestApplication(unittest.TestCase):

    
#     def test_application_application(self):
#         template = mock.Mock()
#         template.parameters = ['un', 'deux', 'trois']
#         stack_info = dict(zip(['zero', 'un', 'deux', 'trois', 'quatre', 'cinq'], range(6)))
#         result = [('un', 1), ('deux', 2), ('trois', 3)]

#         param = cfntemplate.CfnParameters(template, stack_info)

#         self.assertItemsEqual(param, result,
#                               msg="The processed parameters are not valid")

#         representation = repr(param)

#         for k, v in result:
#             self.assertRegexpMatches(
#                 representation, r'%s\s*=\s*%s' % (k, v),
#                 msg="The representation is invalid for key %s" % k)
