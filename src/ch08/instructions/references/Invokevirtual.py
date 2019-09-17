from ch08.instructions.base.Instruction import Index16Instruction
from ch08.rtda.heap.StringPool import StringPool

def _println(stack, descriptor):
    if descriptor == "(Z)V":
        print("{0}".format(stack.pop_numeric() != 0))
    elif descriptor in {"(C)V", "(B)V", "(S)V", "(I)V", "(J)V", "(F)V", "(D)V"}:
        print("{0}".format(stack.pop_numeric()))
    elif descriptor == "(Ljava/lang/String;)V":
        jStr = stack.pop_ref()
        goStr = StringPool.goString(jStr)
        print("{0}".format(goStr))
    else:
        raise RuntimeError("println: " + descriptor)
    stack.pop_ref()

class INVOKE_VIRTURL(Index16Instruction):
    def execute(self, frame):
        from ch08.rtda.heap.MethodLookup import MethodLookup
        from ch08.instructions.base.MethodInvokeLogic import MethodInvokeLogic

        currentClass = frame.method.get_class()
        cp = currentClass.constantPool
        methodRef = cp.get_constant(self.index)
        resolvedMethod = methodRef.resolved_method()
        if resolvedMethod.is_static():
            raise RuntimeError("java.lang.IncompatibleClassChangeError")

        ref = frame.operandStack.get_ref_from_top(resolvedMethod.argSlotCount - 1)
        if not ref:
            if methodRef.name == "println":
                _println(frame.operandStack, methodRef.descriptor)
                return
            raise RuntimeError("java.lang.NullPointerException")

        if resolvedMethod.is_protected() \
                and resolvedMethod.get_class().is_super_class_of(currentClass) \
                and resolvedMethod.get_class().get_package_name() != currentClass.get_package_name() \
                and ref.get_class() != currentClass \
                and not ref.get_class().is_sub_class_of(currentClass):
            raise RuntimeError("java.lang.IllegalAccessError")

        methodToBeInvoked = MethodLookup.lookupMethodInClass(
            ref.get_class(), methodRef.name, methodRef.descriptor)
        if not methodToBeInvoked or methodToBeInvoked.is_abstract():
            raise RuntimeError("java.lang.AbstractMethodError")

        MethodInvokeLogic.invokeMethod(frame, methodToBeInvoked)





