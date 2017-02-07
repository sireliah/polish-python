zaimportuj io
zaimportuj email
zaimportuj unittest
z email.message zaimportuj Message
z test.test_email zaimportuj TestEmailBase


klasa TestCustomMessage(TestEmailBase):

    klasa MyMessage(Message):
        def __init__(self, policy):
            self.check_policy = policy
            super().__init__()

    MyPolicy = TestEmailBase.policy.clone(linesep='boo')

    def test_custom_message_gets_policy_if_possible_from_string(self):
        msg = email.message_from_string("Subject: bogus\n\nmsg\n",
                                        self.MyMessage,
                                        policy=self.MyPolicy)
        self.assertIsInstance(msg, self.MyMessage)
        self.assertIs(msg.check_policy, self.MyPolicy)

    def test_custom_message_gets_policy_if_possible_from_file(self):
        source_file = io.StringIO("Subject: bogus\n\nmsg\n")
        msg = email.message_from_file(source_file,
                                      self.MyMessage,
                                      policy=self.MyPolicy)
        self.assertIsInstance(msg, self.MyMessage)
        self.assertIs(msg.check_policy, self.MyPolicy)

    # XXX add tests dla other functions that take Message arg.


jeżeli __name__ == '__main__':
    unittest.main()
