'''
NOTE(JY): In Transformer.scala, we essentially do a bunch of weird stuff to
get the equivalent of type classes for overloading. I don't think we have to do
that in Python.
'''

from fast.AST import *

def partialEval(f, env={}):
  if isinstance(f, BinaryExpr):
    left = partialEval(f.left, env)
    right = partialEval(f.right, env)
    return facetJoin(left, right, f.opr)
  elif isinstance(f, UnaryExpr):
    sub = partialEval(f.sub, env)
    return facetApply(sub, f.opr)
  elif isinstance(f, Constant):
    return f
  elif isinstance(f, Facet):
    if f.cond.name in env:
      return partialEval(f.thn, env) if env[f.cond.name] else partialEval(f.els, env)
    else:
      true_env = dict(env)
      true_env[f.cond.name] = True
      false_env = dict(env)
      false_env[f.cond.name] = False
      return Facet(f.cond, partialEval(f.thn, true_env),
                           partialEval(f.els, false_env))
  elif isinstance(f, Var):
    if f.name in env:
      return Constant(env[f.name])
    else:
      return Facet(f, Constant(True), Constant(False))
  elif isinstance(f, FObject):
    return f
      
  else:
    raise TypeError("partialEval does not support type %s" % f.__class__.__name__)

def facetApply(f, opr):
  if isinstance(f, Facet):
    return Facet(f.cond, facetApply(f.thn, opr), facetApply(f.els, opr))
  elif isinstance(f, Constant):
    return Constant(opr(f.v))
  elif isinstance(f, FObject):
    return FObject(opr(f.v))

'''
This function should combine two 

NOTE(JY): We should just be able to use the universal Facet constructor
instead of the weird stuff we were doing before... You may need to change
things to get it to work though!
'''
def facetJoin(f0, f1, opr):
  if isinstance(f0, Facet):
    thn = facetJoin(f0.thn, f1, opr)
    els = facetJoin(f0.els, f1, opr)
    return Facet(f0.cond, thn, els)
  elif isinstance(f1, Facet):
    thn = facetJoin(f0, f1.thn, opr)
    els = facetJoin(f0, f1.els, opr)
    return Facet(f1.cond, thn, els)
  else:
    return Constant(opr(f0.v, f1.v))
