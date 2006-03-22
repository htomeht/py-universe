# (C) 2006 Terry Hancock
# errors
"""
Errors and exception handling for PUB.
"""
#--------------------------------------------------------------------
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#--------------------------------------------------------------------

class PubError(Exception):
    """
    Unclassified error in Python Universe Builder.
    """
    # Should be reserved for fatal errors that we won't catch.
    # Base class of all our other errors
    pass

# Top-level errors (generally shouldn't be raised, only caught)

class LinguisticsError(PubError):
    """
    An error occured during language processing (parsing or generation).
    """
    pass

class ParseError(LinguisticsError):
    """
    An error occured in parsing user input.
    """
    pass

class TellError(LinguisticsError):
    """
    An error occured in generated text output.
    """
    pass

class L10nError(LinguisticsError):
    """
    Concept to Word translation error.
    """
    pass

class I18nError(LinguisticsError):
    """
    Word to Concept translation error.
    """
    pass

# Specific errors

class LexicalParseError(ParseError):
    """
    An error occured in reading (lexing) user input.
    """
    # e.g. a misspelled word isn't recognized
    pass

class SyntaxParseError(ParseError):
    """
    An error occured in syntactical tagging of user input.
    """
    # e.g. a word's part-of-speech is ambiguous
    pass

class SemanticError(ParseError):
    """
    An error occured in dereferencing user input to game objects.
    """
    # e.g. nothing seems to match the word
    pass

class SemanticAmbiguityError(ParseError):
    """
    More than one possible interpretation of a word or phrase.
    """
    # e.g. "push button" when there's more than one button in view
    # This should generally result in a "Which do you mean...?"
    pass


    
